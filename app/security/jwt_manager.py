import datetime
from typing import Dict, Optional, Tuple

import jwt
from fastapi import HTTPException

from app.config.settings import settings
from app.schema.token_payload import TokenPayload
from app.security.jwt_params import JWTLifetime, JWTParams
from app.security.jwt_token_type import JWTTokenType
from app.database.redis_client import redis_client


class JWTManager:
    def __init__(
        self,
        jwt_config: JWTParams = JWTParams(
            algorithms=[settings.JWT_ALGORITHM],
            secret_key=settings.JWT_SECRET_KEY,
            lifetime=JWTLifetime(
                for_access=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES,
                for_refresh=settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS,
            ),
        ),
    ):
        self.jwt_config = jwt_config

    async def encode_token(self, payload: TokenPayload, token_type: JWTTokenType = JWTTokenType.ACCESS) -> str:
        expires = (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(minutes=self.jwt_config.lifetime.for_access)
            if token_type == JWTTokenType.ACCESS
            else datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=self.jwt_config.lifetime.for_refresh)
        )

        payload.exp = expires

        return jwt.encode(
            payload=payload.model_dump(exclude_unset=True),
            key=self.jwt_config.secret_key,
            algorithm=self.jwt_config.algorithms[0],
        )

    async def decode_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self.jwt_config.secret_key, algorithms=self.jwt_config.algorithms)
        except:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def verify_access_token(self, token: str) -> dict | None:
        payload = self.decode_token(token)

        user_id = await redis_client.validate_access_token(token)
        if not user_id or user_id != payload.get("user_id"):
            return None
        
        return payload

    async def verify_refresh_token(self, token: str) -> dict | None:
        payload = self.decode_token(token)

        user_id = await redis_client.validate_refresh_token(token)
        if not user_id or user_id != payload.get("user_id"):
            return None
        
        return payload

    async def refresh_access_token(self,refresh_token: str) -> Optional[Tuple[str, str]]:
        payload = await self.verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        user_id = payload["user_id"]
        
        # Создаем новые токены
        new_access, new_refresh = self.create_tokens(user_id)
        
        # Сохраняем в Redis
        await self.store_tokens(user_id, new_access, new_refresh)
        
        # Инвалидируем старый refresh токен
        await redis_client.blacklist_token(refresh_token, 86400)
        
        return new_access, new_refresh


    async def store_tokens(user_id: int, access_token: str, refresh_token:str):
        await redis_client.store_access_token(
            user_id,
            access_token,
            settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES * 60
        )

        await redis_client.store_refresh_token(
            user_id,
            refresh_token,
            settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS * 24 * 60 * 60
        )


    async def logout(self, token: str):
        """Выход из системы (инвалидация токена)"""
        payload = await self.verify_access_token(token)
        if payload:
            await redis_client.revoke_token(token, payload["user_id"])
    
    async def logout_all(user_id: int):
        """Выход со всех устройств"""
        await redis_client.revoke_all_user_tokens(user_id)