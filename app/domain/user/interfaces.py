# app/domain/user/interfaces.py
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.user.models import SysUser
from app.modules.user.schemas import UserCreate, UserUpdate

class AbstractUserService(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> SysUser:
        """获取用户实体（内部使用）"""
        pass

    @abstractmethod
    async def get_user_profile(self, user_id: str) -> dict:
        """获取用户档案"""
        pass

    @abstractmethod
    async def create_user(self, user_in: UserCreate):
        """创建用户"""
        pass

    # 可根据需要继续添加其他抽象方法