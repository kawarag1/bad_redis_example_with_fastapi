from datetime import datetime

from pydantic import BaseModel


class TokenPayload(BaseModel):
    iss: str | None = None
    sub: str
    device_type: str
    device_os: str
    device_browser: str
    device_model: str 
    aud: str | None = None
    exp: datetime | None = None
    nbf: int | None = None
    iat: int | None = None
    jti: str | None = None
