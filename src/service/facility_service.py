from datetime import date

from fastapi import HTTPException

from database.repository.facility_repository import FacilityRepository
from schema.request import FacilityReservationRequest, FacilityReservationConfirmRequest, \
    FacilityMultiReservationRequest, FacilityMultiReservationConfirmRequest
from service.user_service import UserService


class FacilityService:
    def __init__(self, facility_repo: FacilityRepository, user_service: UserService):
        self.facility_repo = facility_repo
        self.user_service = user_service

    async def _check_facility_status(self, facility_id: int):
        status = await self.facility_repo.get_facility_status(facility_id)
        if status is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "FACILITY_NOT_FOUND", "message": "해당 시설을 찾을 수 없습니다."}
            )
        if status == "off":
            raise HTTPException(
                status_code=403,
                detail={"code": "FACILITY_UNAVAILABLE", "message": "해당 시설은 현재 예약이 불가능합니다."}
            )

    async def _check_and_log_facility_usage(self, user_id: str, facility_id: int):
        """하루 동일 시설 이용 여부 체크 후 로그 기록"""
        if await self.facility_repo.has_used_facility_today(user_id, facility_id, date.today()):
            raise HTTPException(
                status_code=403,
                detail={"code": "DAILY_LIMIT_REACHED", "message": "해당 시설은 오늘 이미 이용하셨습니다."}
            )
        await self.facility_repo.log_facility_usage(user_id, facility_id)

    async def reservation(self, request: FacilityReservationRequest):
        await self._check_facility_status(request.facility_id)

        user_check = await self.user_service.find_users_with_name_and_birth(
            name=request.name, birth=request.birth
        )

        if user_check["multiple"]:
            return user_check

        user = user_check["user"]

        await self._check_and_log_facility_usage(user["member_id"], request.facility_id)

        reservation = await self.facility_repo.create_reservation(request.facility_id)
        await self.facility_repo.add_reservation_user(reservation.id, user["member_id"])

        return {"multiple": "false", "message": "예약이 완료되었습니다", "reservation_id": 1}

    async def reserve_confirm(self, request: FacilityReservationConfirmRequest):
        await self._check_facility_status(request.facility_id)

        # 유저 찾기
        user = await self.user_service.find_user_with_name_birth_phone(
            name=request.name,
            birth=request.birth,
            phone=request.phone
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="선택한 전화번호에 해당하는 사용자를 찾을 수 없습니다."
            )

        await self._check_and_log_facility_usage(user["member_id"], request.facility_id)

        # 예약 생성
        reservation = await self.facility_repo.create_reservation(request.facility_id)

        # 예약에 사용자 연결
        await self.facility_repo.add_reservation_user(reservation.id, user["member_id"])

        # 예약에 포함된 사용자 목록
        users = await self.facility_repo.get_reservation_users(reservation.id)

        return {
            "message": "예약이 생성 및 확정되었습니다.",
            "reservation_id": reservation.id,
            "users": users
        }

    async def get_reservations_by_facility(self, facility_id: int):
        reservations = await self.facility_repo.get_reservations_by_facility(facility_id)
        if not reservations:
            return {
                "message": "해당 시설에 예약이 없습니다."
            }
        return reservations

    # 다중 Reserve
    async def multi_reserve(self, request: FacilityMultiReservationRequest):
        await self._check_facility_status(request.facility_id)

        confirm_required = False
        multiple_members_info = []
        unique_multiple_set = set()  # (name, birth) 중복 체크용
        unique_members = []

        for member in request.members:
            user_check = await self.user_service.find_users_with_name_and_birth(
                name=member.name,
                birth=member.birth
            )

            if user_check["multiple"]:
                confirm_required = True
                key = (member.name, str(member.birth))
                if key not in unique_multiple_set:  # 중복된 이름/생년월 제외
                    unique_multiple_set.add(key)
                    multiple_members_info.append({
                        "name": member.name,
                        "birth": member.birth,
                        "candidates": user_check["candidates"]
                    })
            else:
                unique_members.append(user_check["user"])

        if confirm_required:
            return {
                "confirm_required": True,
                "facility_id": request.facility_id,
                "multiple_candidates": multiple_members_info
            }

        reservation = await self.facility_repo.create_reservation(request.facility_id)
        for user in unique_members:
            await self._check_and_log_facility_usage(user["member_id"], request.facility_id)
            await self.facility_repo.add_reservation_user(reservation.id, user["member_id"])

        return {"message": "예약이 완료되었습니다", "reservation_id": reservation.id}

    # 다중 Confirm
    async def multi_confirm(self, request: FacilityMultiReservationConfirmRequest):
        await self._check_facility_status(request.facility_id)

        reservation = await self.facility_repo.create_reservation(request.facility_id)

        for member in request.members:
            user_check = await self.user_service.find_users_with_name_and_birth(
                name=member.name,
                birth=member.birth
            )

            if user_check["multiple"]:
                if not member.phone:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{member.name} (중복된 사용자)의 전화번호가 필요합니다."
                    )
                user = await self.user_service.find_user_with_name_birth_phone(
                    name=member.name,
                    birth=member.birth,
                    phone=member.phone
                )
            else:
                user = user_check["user"]

            await self._check_and_log_facility_usage(user["member_id"], request.facility_id)

            await self.facility_repo.add_reservation_user(reservation.id, user["member_id"])

        return {
            "multiple": False,
            "message": "예약이 확정되었습니다",
            "reservation_id": reservation.id
        }

    async def delete_reservation(self, reservation_id: int):
        deleted = await self.facility_repo.delete_reservation_by_id(reservation_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail={"code": "RESERVATION_NOT_FOUND", "message": "해당 예약을 찾을 수 없습니다."}
            )

        return {"message": "예약이 성공적으로 삭제되었습니다."}

    async def set_facility_status(self, facility_id: int, status: str):
        valid_statuses = ["active", "inactive", "off"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail={"code": "INVALID_STATUS", "message": f"status 값은 {valid_statuses} 중 하나여야 합니다."}
            )

        updated = await self.facility_repo.update_facility_status(facility_id, status)
        if not updated:
            raise HTTPException(
                status_code=404,
                detail={"code": "FACILITY_NOT_FOUND", "message": "해당 시설을 찾을 수 없습니다."}
            )

        return {"message": f"시설 상태가 {status}로 변경되었습니다."}

    async def get_all_facility_statuses(self):
        statuses = await self.facility_repo.get_all_facility_statuses()
        return statuses
