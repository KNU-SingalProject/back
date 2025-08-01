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

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

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

            # ✅ 동명이인 케이스 먼저 체크
            if result.get("multiple"):
                return {
                    "phone_numbers": result.get("phone_numbers", [])
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

            access_token = self.create_jwt(user["member_id"])  # ✅ dict 키 접근
            return JWTResponse(access_token=access_token, name=user["name"])

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

        # 2명 이상 → 전화번호 리스트 반환
        if len(users) > 1:
            return {
                "multiple": True,
                "phone_numbers": [u.phone_num for u in users]
            }

        # 1명 → 이름과 생년월일 반환
        user = users[0]
        return {
            "multiple": False,
            "user": {
                "member_id": user.member_id,
                "name": user.name,
                "birth": user.birth
            }
        }