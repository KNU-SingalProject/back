from sqlalchemy import select, func
from datetime import date

from database.orm import MemberVisit


class MemberVisitRepository:
    def __init__(self, session):
        self.session = session

    async def has_any_visit_today(self, member_ids: list[str]) -> bool:
        """여러 member_id 중 하루 방문 기록이 있는지 체크"""
        if not member_ids:
            return False

        stmt = (
            select(func.count())
            .where(MemberVisit.user_id.in_(member_ids))
            .where(func.date(MemberVisit.visit_time) == func.current_date())  # DB 기준 날짜 비교
        )
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def has_visit_today(self, member_id: str) -> bool:
        """단일 member_id 하루 방문 체크"""
        stmt = (
            select(func.count())
            .where(MemberVisit.user_id == member_id)
            .where(func.date(MemberVisit.visit_time) == func.current_date())
        )
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def add_visit(self, member_id: str):
        """방문 기록 추가"""
        visit = MemberVisit(user_id=member_id)
        self.session.add(visit)
        await self.session.commit()
        await self.session.refresh(visit)
        return visit