from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connector import get_session
from app.schema.request.user_register import UserRegister
from app.schema.response.access_token import AccessToken
from app.schema.response.user_read import UserRead
from app.security.oauth import get_current_user, get_device_dict as get_device
from app.services.user_service import UserService

router = APIRouter(
    prefix="/access"
)

@router.post("/register", response_model=AccessToken)
async def register_user(user_register: UserRegister, device_info = Depends(get_device), session: AsyncSession = Depends(get_session)):
    return await UserService(session).register_user(user_register, device_info)


@router.post("/authorize", response_model=AccessToken)
async def authorize_user(
    username: str = Form(...), password: str = Form(...), device_info = Depends(get_device), session: AsyncSession = Depends(get_session)
):
    return await UserService(session).authorize_user(username, password, device_info)


@router.get("/blacklist")
async def blacklist(user: UserRead = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await UserService(session).blacklist_user(user.id)