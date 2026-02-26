from uuid import UUID

from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None


class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    nickname: Optional[str]
    email: Optional[str]
    roles: list[str] = []