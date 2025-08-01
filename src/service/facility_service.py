from fastapi import HTTPException

from database.repository.facility_repository import FacilityRepository
from database.repository.user_repository import UserRepository
from schema.request import FacilityReservationRequest


class FacilityService:
    def __init__(self, facility_repo: FacilityRepository, user_repo: UserRepository):
        self.facility_repo = facility_repo
        self.user_repo = user_repo

    async def reservation(self, request: FacilityReservationRequest):
        # 유저 확인
        user = await self.user_repo.get_user_by_name_and_birth(
            name=request.name, birth=request.birth
        )
        if not user:
            raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

        # 예약 생성
        reservation = await self.facility_repo.create_reservation(request.facility_id, user.member_id)

        return {"message": "예약이 완료되었습니다", "reservation_id": reservation.id}

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