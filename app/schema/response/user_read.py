from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    id: int
    username: str
    password: str

    model_config = ConfigDict(
        from_attributes=True
    )