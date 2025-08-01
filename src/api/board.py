from fastapi import APIRouter, Depends, UploadFile, Form
from service.board_service import BoardService
from core.di import get_board_service

router = APIRouter(prefix="/board", tags=["Board"])

@router.post("/")
async def create_board(
    title: str = Form(...),
    content: str = Form(...),
    images: list[UploadFile] = [],
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.create_board(title, content, images)

@router.get("/{board_id}")
async def get_board(
    board_id: int,
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.get_board(board_id)

@router.get("/")
async def get_all_boards(
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.get_all_boards()
