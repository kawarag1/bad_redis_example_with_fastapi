import json
from typing import List, Optional

from redis.asyncio import Redis

from app.config.settings import settings

class RedisClient:
    def __init__(self):
        self.redis: Optional[Redis] = None

    
    async def connect(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

        await self.redis.ping()


    async def close(self):
        if self.redis:
            await self.redis.close()

    async def store_access_token(self, user_id: int, token: str, expires_in: int):
        key = f"{settings.JWT_REDIS_PREFIX}access:{token}"
        await self.redis.setex(key, expires_in, str(user_id))
            
        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"
        
        await self.redis.sadd(session_key, token)
        await self.redis.expire(session_key, expires_in * 2)  # Дольше, чем токен
        
    async def store_refresh_token(self, user_id: int, token: str, expires_in: int):
        key = f"{settings.JWT_REDIS_PREFIX}refresh:{token}"
        await self.redis.setex(key, expires_in, str(user_id))

        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"

        await self.redis.sadd(session_key, token)
        await self.redis.expire(session_key, expires_in * 2)

    async def validate_access_token(self, token:str) -> bool:
        if await self.is_token_blacklisted(token):
            return False
        
        key = f"{settings.JWT_REDIS_PREFIX}access:{token}"
        user_id = await self.redis.get(key)
        return int(user_id) if user_id else None
    
    async def validate_refresh_token(self, token: str) -> Optional[int]:
        key = f"{settings.JWT_REDIS_PREFIX}refresh:{token}"
        user_id = await self.redis.get(key)
        return int(user_id) if user_id else None



    
    async def blacklist_token(self, token: str, expires_in: int):
        key = f"{settings.JWT_BLACKLIST_PREFIX}{token}"
        await self.redis.setex(key, expires_in, "blacklisted")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        key = f"{settings.JWT_BLACKLIST_PREFIX}{token}"
        return await self.redis.exists(key) > 0
    

    async def revoke_all_user_tokens(self, user_id: int):
        """Отзыв всех токенов пользователя"""
        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"
        tokens = await self.redis.smembers(session_key)
        
        for token in tokens:
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            access_key = f"{settings.JWT_REDIS_PREFIX}access:{token}"
            refresh_key = f"{settings.JWT_REDIS_PREFIX}refresh:{token}"

            access_ttl = await self.redis.ttl(access_key)
            refresh_ttl = await self.redis.ttl(refresh_key)


            if access_ttl > 0:
                await self.blacklist_token(token, access_ttl)
            
            if refresh_ttl > 0:
                await self.blacklist_token(token, refresh_ttl)
            
            # Удаляем из хранилища токенов
            await self.redis.delete(access_key, refresh_key)
        
        # Удаляем сессию
        await self.redis.delete(session_key)
    
    async def revoke_token(self, token: str, user_id: int):
        """Отзыв конкретного токена"""
        # Добавляем в черный список
        await self.blacklist_token(token, 86400)
        # Удаляем из хранилища
        await self.redis.delete(f"{settings.JWT_REDIS_PREFIX}access:{token}")
        
        # Удаляем из сессий пользователя
        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"
        await self.redis.srem(session_key, token)
    
    async def get_user_active_sessions(self, user_id: int) -> List[str]:
        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"
        tokens = await self.redis.smembers(session_key)
        return list(tokens)

redis_client = RedisClient()