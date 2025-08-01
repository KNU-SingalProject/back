from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.connection import get_postgres_db
from database.repository.facility_repository import FacilityRepository
from service.facility_service import FacilityService
from service.user_service import UserService
from database.repository.user_repository import UserRepository

# ------------------- 리포지토리 관련 DI -------------------
def get_user_repo(session: AsyncSession = Depends(get_postgres_db)) -> UserRepository:
    return UserRepository(session)

# ------------------- 서비스 관련 DI -------------------
def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)

def get_facility_repo(session: AsyncSession = Depends(get_postgres_db)) -> FacilityRepository:
    return FacilityRepository(session)

# ------------------- 서비스 관련 DI -------------------
def get_facility_service(
    facility_repo: FacilityRepository = Depends(get_facility_repo),
    user_service: UserService = Depends(get_user_service)
) -> FacilityService:
    return FacilityService(facility_repo, user_service)