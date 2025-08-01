from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.connection import get_postgres_db
from database.repository.board_repository import BoardRepository
from database.repository.facility_repository import FacilityRepository
from database.repository.visit_repository import MemberVisitRepository
from service.board_service import BoardService
from service.facility_service import FacilityService
from service.user_service import UserService
from database.repository.user_repository import UserRepository

# ------------------- 리포지토리 관련 DI -------------------
def get_user_repo(session: AsyncSession = Depends(get_postgres_db)) -> UserRepository:
    return UserRepository(session)

def get_visit_repo(session: AsyncSession = Depends(get_postgres_db)) -> MemberVisitRepository:  # ✅ 추가
    return MemberVisitRepository(session)

def get_board_repo(session: AsyncSession = Depends(get_postgres_db)) -> BoardRepository:
    return BoardRepository(session)
# ------------------- 서비스 관련 DI -------------------
def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    visit_repo: MemberVisitRepository = Depends(get_visit_repo)  # ✅ 추가
) -> UserService:
    return UserService(user_repo, visit_repo)  # ✅ visit_repo 주입

def get_facility_repo(session: AsyncSession = Depends(get_postgres_db)) -> FacilityRepository:
    return FacilityRepository(session)

def get_facility_service(
    facility_repo: FacilityRepository = Depends(get_facility_repo),
    user_service: UserService = Depends(get_user_service)
) -> FacilityService:
    return FacilityService(facility_repo, user_service)

def get_board_service(
    board_repo: BoardRepository = Depends(get_board_repo)
) -> BoardService:
    return BoardService(board_repo)
