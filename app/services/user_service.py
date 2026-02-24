from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repos.user_repository import UserRepository
from app.schema.request.user_register import UserRegister
from app.schema.response.access_token import AccessToken
from app.schema.token_payload import TokenPayload
from app.security.jwt_manager import JWTManager
from app.security.jwt_token_type import JWTTokenType
from app.database.redis_client import redis_client


class UserService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._user_repository = UserRepository(session)

    async def get_user_tokens(self, **kwargs) -> AccessToken:
        token_payload = TokenPayload(**kwargs)
        jwt_manager = JWTManager()

        return AccessToken(
            access_token=await jwt_manager.encode_token(token_payload, JWTTokenType.ACCESS),
            refresh_token=await jwt_manager.encode_token(token_payload, JWTTokenType.REFRESH),
        )

    async def register_user(self, user_register: UserRegister) -> AccessToken:
        existing_user = await self._user_repository.ensure_exists(username=user_register.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Такой игрок уже зарегистрирован!")

        user = await self._user_repository.create(
            **user_register.model_dump(exclude={"password"}, exclude_unset=True),
            password=user_register.password,
        )
        tokens = await self.get_user_tokens(sub=str(user.id))
        await JWTManager.store_tokens(user.id, tokens.access_token, tokens.refresh_token)
        return tokens

    async def authorize_user(self, username: str, password: str) -> AccessToken:
        user = await self._user_repository.get_by_filter_one(username=username)

        if not user:
            raise HTTPException(status_code=400, detail="Пользователь с такими именем и фамилией не найден.")

        return await self.get_user_tokens(sub=str(user.id))
