from pydantic import BaseModel


class JWTLifetime(BaseModel):
    for_access: int
    for_refresh: int


class JWTParams(BaseModel):
    algorithms: list[str]
    secret_key: str
    lifetime: JWTLifetime