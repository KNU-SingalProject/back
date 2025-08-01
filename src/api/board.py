from fastapi import APIRouter, Depends, UploadFile, Form
from service.board_service import BoardService
from core.di import get_board_service

router = APIRouter(prefix="/board", tags=["Board"])

@router.post("", status_code=201)
async def create_board(
    title: str = Form(...),
    content: str = Form(...),
    images: list[UploadFile] = [],
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.create_board(title, content, images)

@router.get("/{board_id}", status_code=200)
async def get_board(
    board_id: int,
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.get_board(board_id)

@router.get("", status_code=200)
async def get_all_boards(
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.get_all_boards()

@router.patch("/{board_id}", status_code=200)
async def update_board(
    board_id: int,
    title: str | None = Form(None),
    content: str | None = Form(None),
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.update_board(board_id, title, content)


@router.delete("/{board_id}", status_code=204)
async def delete_board(
    board_id: int,
    board_service: BoardService = Depends(get_board_service)
):
    return await board_service.delete_board(board_id)