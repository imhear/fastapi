from uuid import UUID

from pydantic import BaseModel, field_serializer
from typing import Optional, List


class RoleBase(BaseModel):
    name: str
    code: str
    status: int = 1


class RoleCreate(RoleBase):
    permission_ids: Optional[List[str]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[int] = None
    permission_ids: Optional[List[str]] = None


class RoleResponse(RoleBase):
    id: UUID

    class Config:
        from_attributes = True