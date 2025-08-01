from fastapi import HTTPException, Request
from jose import jwt, JWTError
from datetime import datetime, timedelta, date

from database.repository.user_repository import UserRepository
from core.config import settings
from database.orm import User
from schema.request import SignUpRequest, LogInRequest
from schema.response import JWTResponse


class UserService:

    encoding = "UTF-8"
    secret_key = settings.JWT_SECRET_KEY.get_secret_value()
    jwt_algorithm = "HS256"

    def __init__(self, user_repo: UserRepository, visit_repo):
        self.user_repo = user_repo
        self.visit_repo = visit_repo

    def create_jwt(self, member_id: str) -> str:
        return jwt.encode(
            {
                "sub": member_id,
                "exp": datetime.now() + timedelta(days=1),
            },
            self.secret_key,
            algorithm=self.jwt_algorithm,
        )

    def decode_jwt(self, access_token: str) -> str:
        try:
            payload: dict = jwt.decode(
                access_token, self.secret_key, algorithms=[self.jwt_algorithm]
            )
            member_id = payload.get("sub")

            if member_id is None:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "code": "TOKEN_EXPIRED",
                        "message": "토큰이 유효하지 않거나 만료되었습니다"
                    }
                )

            return member_id

        except JWTError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "TOKEN_EXPIRED",
                    "message": "토큰이 유효하지 않거나 만료되었습니다"
                }
            )

    async def get_user_by_token(self, access_token: str, req: Request) -> User:
        member_id: str = self.decode_jwt(access_token)
        user: User | None = await self.user_repo.get_user_by_memberid(member_id=member_id)

        if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "해당 유저를 찾을 수 없습니다"
                }
            )
        return user

    async def sign_up(self, request: SignUpRequest):
        try:
            if await self.user_repo.get_user_by_phone_num(request.phone_num):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "PHONE_NUM_CONFLICT",
                        "message": "이미 사용 중인 전화번호입니다"
                    }
                )
            if await self.user_repo.get_user_by_memberid(request.member_id):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "MEMBER_ID_CONFLICT",
                        "message": "이미 사용 중인 고유번호입니다"
                    }
                )

            user = User.create(
                member_id=request.member_id,
                name=request.name,
                gender=request.gender,
                birth=request.birth,
                phone_num=request.phone_num
            )

            await self.user_repo.save_user(user)

            return {"message": "회원가입이 완료되었습니다"}

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"예기치 못한 오류 발생: {str(e)}"
                }
            )

    async def log_in(self, request: LogInRequest, req: Request):
        try:
            result = await self.find_users_with_name_and_birth(
                name=request.name,
                birth=request.birth
            )

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "해당 이름과 생년으로 사용자를 찾을 수 없습니다."
                    }
                )

            member_ids = []
            if result.get("multiple"):
                member_ids = [c["member_id"] for c in result.get("candidates", [])]
            elif result.get("user"):
                member_ids = [result["user"]["member_id"]]

            # ✅ 하루 방문 체크
            already_visited_today = await self.visit_repo.has_any_visit_today(member_ids)
            if already_visited_today:
                return {
                    "multiple": result.get("multiple", False),
                    "phone_numbers": [c["phone"] for c in result.get("candidates", [])] if result.get(
                        "multiple") else [],
                    "visit_log": True
                }

            # ✅ 동명이인 케이스 먼저 체크
            if result.get("multiple"):
                phone_numbers = [c["phone"] for c in result.get("candidates", [])]
                return {
                    "multiple": True,
                    "phone_numbers": phone_numbers,
                    "message": "첫 로그인 - 방문 등록 전 단계"
                }

            # ✅ 한 명만 있는 경우 처리
            user = result.get("user")
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "사용자 정보가 없습니다."
                    }
                )

            await self.visit_repo.add_visit(user["member_id"])

            access_token = self.create_jwt(user["member_id"])
            return {
                "access_token": access_token,
                "name": user["name"],
                "message": "로그인 성공 및 방문 등록 완료"
            }

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"예기치 못한 오류 발생: {str(e)}"
                }
            )


    async def find_users_with_name_and_birth(self, name: str, birth: date):
        users = await self.user_repo.get_user_by_name_and_birth(name=name, birth=birth)

        if not users:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "해당 이름과 생년월일의 사용자가 없습니다."
                }
            )

        # 2명 이상 → 후보 리스트(candidates) 반환
        if len(users) > 1:
            return {
                "multiple": True,
                "candidates": [
                    {
                        "member_id": u.member_id,
                        "name": u.name,
                        "birth": u.birth,
                        "phone": u.phone_num
                    }
                    for u in users
                ]
            }

        # 1명 → 단일 유저 반환
        user = users[0]
        return {
            "multiple": False,
            "user": {
                "member_id": user.member_id,
                "name": user.name,
                "birth": user.birth,
                "phone": user.phone_num
            }
        }

    async def find_user_with_name_birth_phone(self, name: str, birth: date, phone: str):
        user = await self.user_repo.get_user_by_name_birth_phone(name, birth, phone)

        if not user:
            return None

        return {
            "member_id": user.member_id,
            "name": user.name,
            "birth": user.birth,
            "phone_num": user.phone_num
        }

    async def get_all_users(self, skip: int = 0, limit: int = 100, name: str | None = None):
        users = await self.user_repo.get_all_users(skip=skip, limit=limit, name=name)
        return [
            {
                "member_id": u.member_id,
                "name": u.name,
                "gender": u.gender,
                "birth": u.birth,
                "age": u.age,
                "phone_num": u.phone_num,
                "created_at": u.created_at
            }
            for u in users
        ]