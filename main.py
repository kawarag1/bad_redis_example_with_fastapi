from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.main_router import router
from app.utils.migration import migrate
from app.database.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await migrate()
    await redis_client.connect()
    yield


app = FastAPI(title="Сервис авторизации и регистрации iCore", root_path="/api/auth", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
