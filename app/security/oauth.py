from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse 

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

async def get_device_dict(request: Request) -> dict:
    """Возвращает словарь с информацией об устройстве"""
    user_agent = request.headers.get("user-agent", "")
    ua = parse(user_agent) if user_agent else None
    
    # Определяем тип клиента
    if request.headers.get("x-client-type") == "mobile_app":
        device_type = "mobile_app"
    elif request.headers.get("x-client-type") == "desktop_app":
        device_type = "desktop_app"
    elif ua and ua.is_mobile:
        device_type = "mobile_web"
    elif ua and ua.is_tablet:
        device_type = "tablet_web"
    elif ua and ua.is_pc:
        device_type = "desktop_web"
    elif ua and ua.is_bot:
        device_type = "bot"
    else:
        device_type = "unknown"
    
    return {
        "type": device_type,
        "os": ua.os.family if ua and ua.os.family else "unknown",
        "os_version": ua.os.version_string if ua and ua.os.version_string else "unknown",
        "browser": ua.browser.family if ua and ua.browser.family else "unknown",
        "browser_version": ua.browser.version_string if ua and ua.browser.version_string else "unknown",
        "device": ua.device.family if ua and ua.device.family else "unknown",
        "is_mobile": ua.is_mobile if ua else False,
        "is_tablet": ua.is_tablet if ua else False,
        "is_pc": ua.is_pc if ua else False,
        "is_bot": ua.is_bot if ua else False
    }