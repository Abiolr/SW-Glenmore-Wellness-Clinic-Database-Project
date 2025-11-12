from pydantic import BaseModel
from typing import Optional


class LoginPayload(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
