import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine
from app.models import Base
from app.routers import auth, teams, tasks, messages

# DB 자동 마이그레이션
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API", version="1.0.0")

# CORS
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터
app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(messages.router)

# 정적 파일 서빙 (프론트엔드)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "app", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def root():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
