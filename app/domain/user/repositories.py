"""
用户模块仓储抽象层
app/domain/user/repositories.py
"""
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.user.models import User

class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, session: AsyncSession, user: User) -> User:
        pass

    @abstractmethod
    async def update(self, session: AsyncSession, obj: User) -> User:
        pass

    # 其他方法...