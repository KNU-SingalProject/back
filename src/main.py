from fastapi import FastAPI
from api import user, facility, board

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://KNU-SingalProject.github.io",
    "https://knu-singalproject.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],  # 배포 시에는 특정 도메인만
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(facility.router)
app.include_router(board.router)
@app.get("/")
async def root():
    return {"message": "Hello World"}