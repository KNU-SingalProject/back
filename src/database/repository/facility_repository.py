from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import delete
from sqlalchemy.sql.functions import func

from database.orm import FacilityReservation, ReservationUser, User, Facility, FacilityStatus, MemberFacility


class FacilityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reservation(self, facility_id: int):
        reservation = FacilityReservation(facility_id=facility_id)
        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def add_reservation_user(self, reservation_id: int, user_id: str):
        reservation_user = ReservationUser(reservation_id=reservation_id, user_id=user_id)
        self.session.add(reservation_user)
        await self.session.commit()
        return reservation_user

    async def get_reservation_users(self, reservation_id: int):
        result = await self.session.execute(
            select(User.member_id, User.name)
            .join(ReservationUser, ReservationUser.user_id == User.member_id)
            .where(ReservationUser.reservation_id == reservation_id)
        )
        return [{"member_id": r[0], "name": r[1]} for r in result.fetchall()]

    async def get_reservations_by_facility(self, facility_id: int):
        from sqlalchemy.future import select

        result = await self.session.execute(
            select(
                FacilityReservation.id,
                User.name
            )
            .join(ReservationUser, ReservationUser.reservation_id == FacilityReservation.id)
            .join(User, User.member_id == ReservationUser.user_id)
            .where(FacilityReservation.facility_id == facility_id)
        )

        rows = result.fetchall()
        if not rows:
            return []

        reservations = {}
        for r_id, user_name in rows:
            if r_id not in reservations:
                reservations[r_id] = {
                    "reservation_id": r_id,
                    "users": []
                }
            reservations[r_id]["users"].append(user_name)

        return list(reservations.values())

    async def delete_reservation_by_id(self, reservation_id: int) -> bool:
        stmt = delete(FacilityReservation).where(FacilityReservation.id == reservation_id)
        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            return False  # 삭제된 행이 없으면 False 반환

        await self.session.commit()
        return True

    async def get_facility_status(self, facility_id: int) -> str:
        stmt = (
            select(FacilityStatus.status)
            .where(FacilityStatus.facility_id == facility_id)
        )
        result = await self.session.execute(stmt)
        status = result.scalar_one_or_none()
        return status

    async def update_facility_status(self, facility_id: int, status: str) -> bool:
        stmt = (
            update(FacilityStatus)
            .where(FacilityStatus.facility_id == facility_id)
            .values(status=status)
        )
        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            # 없으면 새로 생성
            new_status = FacilityStatus(facility_id=facility_id, status=status)
            self.session.add(new_status)
            await self.session.commit()
            return True

        await self.session.commit()
        return True

    async def get_all_facility_statuses(self):
        stmt = select(FacilityStatus.facility_id, FacilityStatus.status)
        result = await self.session.execute(stmt)
        rows = result.all()
        return [{"facility_id": r.facility_id, "status": r.status} for r in rows]

    async def has_used_facility_today(self, user_id: str, facility_id: int, usage_date: date) -> bool:
        stmt = (
            select(MemberFacility)
            .where(MemberFacility.user_id == user_id)
            .where(MemberFacility.facility_id == facility_id)
            .where(MemberFacility.usage_date == usage_date)
        )
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def log_facility_usage(self, user_id: str, facility_id: int):
        log = MemberFacility(
            user_id=user_id,
            facility_id=facility_id,
            usage_date=date.today()
        )
        self.session.add(log)
        await self.session.commit()