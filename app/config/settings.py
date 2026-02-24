from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from yarl import URL


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PATH: str

    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_LIFETIME_MINUTES: int
    JWT_REFRESH_TOKEN_LIFETIME_DAYS: int

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    JWT_REDIS_PREFIX: str = "jwt:"
    JWT_BLACKLIST_PREFIX: str = "blacklist:"
    JWT_USER_SESSIONS_PREFIX: str = "user_sessions:"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def db_url(self):
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            path=f"/{self.POSTGRES_PATH}",
        )


@lru_cache
def create_settings_instance() -> Settings:
    return Settings()


settings: Settings = Settings()
