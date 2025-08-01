from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import func

from database.orm import FacilityReservation, ReservationUser, User


class FacilityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_facility_reservation(self, facility_id: int):
        stmt = select(FacilityReservation).where(FacilityReservation.facility_id == facility_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_reservation(self, facility_id: int, user_id: str):
        # FacilityReservation 생성
        reservation = FacilityReservation.create(facility_id)
        self.session.add(reservation)
        await self.session.flush()  # reservation.id 확보

        # ReservationUser 생성
        reservation_user = ReservationUser.create(reservation.id, user_id)
        self.session.add(reservation_user)

        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def add_reservation_user(self, reservation_id: int, user_id: str):
        reservation_user = ReservationUser(reservation_id=reservation_id, user_id=user_id)
        self.session.add(reservation_user)
        await self.session.commit()
        return reservation_user

    async def count_reservation_users(self, facility_id: int):
        stmt = (
            select(func.count(ReservationUser.id))
            .join(FacilityReservation)
            .where(FacilityReservation.facility_id == facility_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_reservation_users(self, reservation_id: int):
        stmt = (
            select(User)
            .join(ReservationUser, ReservationUser.user_id == User.member_id)
            .where(ReservationUser.reservation_id == reservation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()