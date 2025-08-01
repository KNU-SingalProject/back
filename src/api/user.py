from fastapi import APIRouter, Depends, Request
from datetime import date

from schema.request import SignUpRequest, LogInRequest
from service.user_service import UserService
from core.di import get_user_service

router = APIRouter(prefix="/users", tags=["User"])

@router.post("/sign-up", status_code=201)
async def user_sign_up(
        request: SignUpRequest,
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.sign_up(request)

@router.post("/log-in", status_code=200)
async def user_log_in(
        request: LogInRequest,
        req: Request,
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.log_in(request, req)

@router.get("/search", status_code=200)
async def search_users(
        name: str,
        birth: date,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.find_users_with_name_and_birth(name, birth)