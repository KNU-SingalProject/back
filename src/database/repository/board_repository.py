from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.orm import Board, BoardImage

class BoardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_board(self, title: str, content: str) -> Board:
        board = Board(title=title, content=content)
        self.session.add(board)
        await self.session.commit()
        await self.session.refresh(board)
        return board

    async def add_board_images(self, board_id: int, image_urls: list[str]):
        images = [BoardImage(board_id=board_id, image_url=url) for url in image_urls]
        self.session.add_all(images)
        await self.session.commit()

    async def get_board(self, board_id: int) -> Board | None:
        result = await self.session.execute(select(Board).where(Board.id == board_id))
        return result.scalar_one_or_none()

    async def get_all_boards(self) -> list[Board]:
        result = await self.session.execute(select(Board))
        return result.scalars().all()