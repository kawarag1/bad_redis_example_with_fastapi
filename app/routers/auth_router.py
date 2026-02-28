from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connector import get_session
from app.schema.request.user_register import UserRegister
from app.schema.response.access_token import AccessToken
from app.schema.response.user_read import UserRead
from app.security.oauth import get_current_user
from app.services.user_service import UserService

router = APIRouter(
    prefix="/access"
)

@router.post("/register", response_model=AccessToken)
async def register_user(user_register: UserRegister, session: AsyncSession = Depends(get_session)):
    return await UserService(session).register_user(user_register)


@router.post("/authorize", response_model=AccessToken)
async def authorize_user(
    username: str = Form(...), password: str = Form(...), session: AsyncSession = Depends(get_session)
):
    return await UserService(session).authorize_user(username, password)


@router.get("/blacklist")
async def blacklist(user: UserRead = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await UserService(session).blacklist_user(user.id)