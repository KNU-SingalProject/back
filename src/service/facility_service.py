from fastapi import HTTPException

from database.repository.facility_repository import FacilityRepository
from database.repository.user_repository import UserRepository
from schema.request import FacilityReservationRequest
from service.user_service import UserService


class FacilityService:
    def __init__(self, facility_repo: FacilityRepository, user_service: UserService):
        self.facility_repo = facility_repo
        self.user_service = user_service


    async def reservation(self, request: FacilityReservationRequest):
        user_check = await self.user_service.find_users_with_name_and_birth(
            name=request.name, birth=request.birth
        )

        if user_check["multiple"]:
            return user_check

        user = user_check["user"]

        reservation = await self.facility_repo.create_reservation(request.facility_id)
        await self.facility_repo.add_reservation_user(reservation.id, user.member_id)

        users = await self.facility_repo.get_reservation_users(reservation.id)
        return {
            "message": "예약이 완료되었습니다",
            "reservation_id": reservation.id,
            "users": users
        }

    async def add_user(self, reservation_id: int, user_id: str):
        count = await self.facility_repo.count_reservation_users(reservation_id)
        if count >= 4:
            raise HTTPException(status_code=400, detail="예약 인원은 최대 4명입니다.")

        await self.facility_repo.add_reservation_user(reservation_id, user_id)
        users = await self.facility_repo.get_reservation_users(reservation_id)

        return {
            "reservation_id": reservation_id,
            "users": users
        }

    async def get_reservation_list(self, facility_id: int):
        # 시설 예약 가져오기
        reservation = await self.facility_repo.get_facility_reservation(facility_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="예약이 존재하지 않습니다")

        # 예약자 명단 가져오기
        reservation_users = await self.facility_repo.get_reservation_users(reservation.id)
        return {
            "facility_id": facility_id,
            "reservation_id": reservation.id,
            "users": [{"name": u.name, "member_id": u.member_id} for u in reservation_users]
        }