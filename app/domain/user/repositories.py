# app/domain/user/repositories.py
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.user.models import SysUser

class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, session: AsyncSession, user_id: str) -> Optional[SysUser]:
        pass

    @abstractmethod
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[SysUser]:
        pass

    @abstractmethod
    async def create(self, session: AsyncSession, user: SysUser) -> SysUser:
        pass

    @abstractmethod
    async def update(self, session: AsyncSession, user: SysUser) -> SysUser:
        pass

    # 其他方法...