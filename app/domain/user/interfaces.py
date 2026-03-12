"""
用户模块服务抽象层
app/domain/user/interfaces.py
"""
from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.models import User
from app.modules.user.schemas import UserCreate, UserUpdate

class AbstractUserService(ABC):
    @abstractmethod
    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """根据 ID 获取用户 ORM 对象，若不存在返回 None"""
        pass

    @abstractmethod
    async def get_user_profile(self, user_id: int) -> dict:
        """获取用户档案"""
        pass

    @abstractmethod
    async def create_user(self, user_in: UserCreate):
        """创建用户"""
        pass

    @abstractmethod
    async def update_user(self, session, user_id, user_update, current_version, current_user_id):
        pass

    @abstractmethod
    async def get_user_by_username(self, session, username):
        pass

    @abstractmethod
    async def update_password(self, session, id, new_password):
        pass

