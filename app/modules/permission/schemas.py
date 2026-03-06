from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class PermissionBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: str = 'general'
    is_active: bool = True


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    id: UUID

    class Config:
        from_attributes = True