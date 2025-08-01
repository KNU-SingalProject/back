# service/board_service.py
import uuid
from fastapi import HTTPException, UploadFile
from database.repository.board_repository import BoardRepository
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from core.config import settings  # AWS_KEY, AWS_SECRET, AWS_BUCKET 등 환경변수

class BoardService:
    def __init__(self, board_repo: BoardRepository):
        self.board_repo = board_repo
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
            region_name="ap-northeast-2"
        )

    async def upload_to_s3(self, file: UploadFile) -> str:
        try:
            file_key = f"board/{uuid.uuid4()}_{file.filename}"
            self.s3_client.upload_fileobj(
                file.file,
                settings.AWS_BUCKET_NAME,
                file_key,
            )
            return f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
        except (BotoCoreError, NoCredentialsError) as e:
            raise HTTPException(status_code=500, detail=f"S3 업로드 실패: {str(e)}")

    async def create_board(self, title: str, content: str, images: list[UploadFile]):
        # 게시글 생성
        board = await self.board_repo.create_board(title, content)

        # 이미지 S3 업로드
        image_urls = []
        if images:
            for img in images:
                url = await self.upload_to_s3(img)
                image_urls.append(url)
            await self.board_repo.add_board_images(board.id, image_urls)

        return {
            "message": "게시글이 등록되었습니다.",
            "board_id": board.id
        }

    async def get_board(self, board_id: int):
        board = await self.board_repo.get_board(board_id)
        if not board:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        return board

    async def get_all_boards(self):
        return await self.board_repo.get_all_boards()

    async def update_board(self, board_id: int, title: str | None, content: str | None):
        board = await self.board_repo.update_board(board_id, title, content)
        if not board:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        return {"message": "게시글이 수정되었습니다.", "board_id": board.id}

    async def delete_board(self, board_id: int):
        # 게시글 확인
        board = await self.board_repo.get_board(board_id)
        if not board:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        # 이미지 URL 조회
        image_urls = await self.board_repo.get_board_images(board_id)

        # S3 이미지 삭제
        for url in image_urls:
            try:
                key = url.split(f"{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/")[-1]
                self.s3_client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)
            except Exception as e:
                print(f"S3 이미지 삭제 실패: {url}, {e}")

        # DB 게시글 삭제
        deleted = await self.board_repo.delete_board(board_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="게시글 삭제 중 오류가 발생했습니다.")

        return {"message": "게시글과 이미지가 삭제되었습니다.", "board_id": board_id}