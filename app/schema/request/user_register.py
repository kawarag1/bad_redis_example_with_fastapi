from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username: str = Field(examples=["yourUsername"])
    password: str = Field(examples=["my_secret_password"])