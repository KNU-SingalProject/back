from fastapi import HTTPException

from database.repository.facility_repository import FacilityRepository
from database.repository.user_repository import UserRepository
from schema.request import FacilityReservationRequest, FacilityMultiReservationRequest, ConfirmUserRequest, \
    FacilityReservationConfirmRequest
from service.user_service import UserService


class FacilityService:
    def __init__(self, facility_repo: FacilityRepository, user_service: UserService):
        self.facility_repo = facility_repo
        self.user_service = user_service

    async def reserve_check(self, request: FacilityReservationRequest):
        result = await self.user_service.find_users_with_name_and_birth(
            name=request.name,
            birth=request.birth
        )

        # ✅ 동명이인 있는 경우
        if result.get("multiple"):
            return {
                "multiple": True,
                "message": "동일 이름과 생년월일 사용자가 여러 명 있습니다. 전화번호를 선택하세요.",
                "phone_numbers": result.get("phone_numbers", [])
            }

        # ✅ 유저 1명인 경우 바로 예약 확정
        user = result.get("user")
        if not user:
            raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

        reservation = await self.facility_repo.create_reservation(request.facility_id)
        await self.facility_repo.add_reservation_user(reservation.id, user.member_id)

        users = await self.facility_repo.get_reservation_users(reservation.id)
        return {
            "multiple": False,
            "message": "예약이 완료되었습니다.",
            "reservation_id": reservation.id,
            "users": users
        }

    async def reserve_confirm(self, request: FacilityReservationConfirmRequest):
        # 전화번호까지 포함해서 유저 찾기
        user = await self.user_service.find_user_with_name_birth_phone(
            name=request.name,
            birth=request.birth,
            phone=request.phone
        )

        if not user:
            raise HTTPException(status_code=404, detail="선택한 전화번호에 해당하는 사용자를 찾을 수 없습니다.")

        reservation = await self.facility_repo.create_reservation(request.facility_id)
        await self.facility_repo.add_reservation_user(reservation.id, user.member_id)

        users = await self.facility_repo.get_reservation_users(reservation.id)
        return {
            "message": "예약이 확정되었습니다.",
            "reservation_id": reservation.id,
            "users": users
        }