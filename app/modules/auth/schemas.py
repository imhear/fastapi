# app/modules/auth/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List


class LoginRequest(BaseModel):
    username: str
    password: str
    captchaId: Optional[str] = ""
    captchaCode: Optional[str] = ""
    tenantId: Optional[int] = None


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"
    expiresIn: int


class RefreshRequest(BaseModel):
    refreshToken: str


class TokenPayload(BaseModel):
    sub: str  # user id
    exp: Optional[int] = None
    type: Optional[str] = None


class Message(BaseModel):
    message: str


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=40)