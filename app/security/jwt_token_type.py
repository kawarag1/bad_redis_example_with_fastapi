from enum import Enum


class JWTTokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"