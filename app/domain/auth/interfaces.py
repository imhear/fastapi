# app/domain/auth/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.models import SysUser


class AbstractAuthService(ABC):
    @abstractmethod
    async def authenticate_user(self, session: AsyncSession, username: str, password: str) -> Optional[SysUser]:
        """认证用户，成功返回用户对象，失败返回 None"""
        pass