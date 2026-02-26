# app/modules/role/interfaces.py
from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.role.schemas import RoleResponse

class AbstracRoleSercice(ABC):
    @abstractmethod
    async def list_roles(self, db: AsyncSession) -> List[RoleResponse]:
        pass