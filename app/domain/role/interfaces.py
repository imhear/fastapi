# app/domain/role/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.role.schemas import RoleResponse

class AbstractRoleService(ABC):
    @abstractmethod
    async def list_roles(self) -> List[RoleResponse]:
        """列出所有角色"""
        pass

    @abstractmethod
    async def get_role_options(self,) -> List[dict]:
        """获取角色下拉选项"""
        pass

    # 可根据需要添加其他方法