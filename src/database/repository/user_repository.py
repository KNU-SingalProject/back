from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import Any, Optional

from database.orm import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_user_by_fieldf(self, field_name: str, value: Any) -> Optional[User]:
        try:
            field = getattr(User, field_name)
            stmt: Select = select(User).where(field == value)
            result = await self.session.execute(stmt)
            return result.scalars().one_or_none()

        except SQLAlchemyError as e:
            print(f"DB 조회 오류: {e}")
            raise

        except Exception as e:
            print(f"예기치 못한 오류: {e}")
            raise

    async def get_user_by_memberid(self, member_id: str) -> Optional[User]:
        return await self._get_user_by_fieldf("member_id", member_id)

    async def get_user_by_phone_num(self, phone_num: str) -> Optional[User]:
        return await self._get_user_by_fieldf("phone_num", phone_num)

    async def get_user_by_name_and_birth(self, name: str, birth: str) -> Optional[User]:
        try:
            stmt: Select = select(User).where(
                User.name == name,
                User.birth == birth
            )
            result = await self.session.execute(stmt)
            return result.scalars().one_or_none()
        except SQLAlchemyError as e:
            print(f"DB 조회 오류: {e}")
            raise
        except Exception as e:
            print(f"예기치 못한 오류: {e}")
            raise

    async def save_user(self, user: User) -> User:
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        except SQLAlchemyError as e:
            print(f"DB 저장 오류: {e}")
            raise

        except Exception as e:
            print(f"예기치 못한 오류: {e}")
            raise
