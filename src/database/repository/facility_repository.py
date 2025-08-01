from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import func

from database.orm import FacilityReservation, ReservationUser, User, Facility


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