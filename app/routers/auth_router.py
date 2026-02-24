from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connector import get_session
from app.schema.request.user_register import UserRegister
from app.schema.response.access_token import AccessToken
from app.services.user_service import UserService

router = APIRouter(
    prefix="/auth"
)

@router.post("/register", response_model=AccessToken)
async def register_user(user_register: UserRegister, session: AsyncSession = Depends(get_session)):
    return await UserService(session).register_user(user_register)


@router.post("/authorize", response_model=AccessToken)
async def authorize_user(
    username: str = Form(...), password: str = Form(...), session: AsyncSession = Depends(get_session)
):
    return await UserService(session).authorize_user(username, password)
