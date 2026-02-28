from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connector import get_session
from app.database.repos.user_repository import UserRepository
from app.schema.response.user_read import UserRead
from app.security.jwt_manager import JWTManager
from app.database.redis_client import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/access/authorize")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    if await redis_client.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    data = await JWTManager().decode_token(token)

    user_id = data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера, попробуйте позже.",
        )
    user = await UserRepository(session).get_by_id(int(user_id))
    return UserRead.model_validate(user)