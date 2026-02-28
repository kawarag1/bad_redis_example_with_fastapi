from fastapi import APIRouter

from app.routers.auth_router import router as auth_router

router = APIRouter(
    prefix="/v1"
)

router.include_router(auth_router)