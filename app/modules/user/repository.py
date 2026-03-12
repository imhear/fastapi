"""
用户模块仓储层
app/modules/user/repository.py
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.user.repositories import AbstractUserRepository
from app.modules.user.models import User
from app.modules.user.schemas import UserCreate, UserUpdate


class SQLAlchemyUserRepository(AbstractUserRepository):
    async def get_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id, User.is_deleted == 0)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username, User.is_deleted == 0)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def update(self, session: AsyncSession, obj: User) -> Optional[User]:
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, user_id: str) -> bool:
        user = await self.get_by_id(session=session, user_id=user_id)
        if not user:
            return False
        user.is_deleted = 1
        session.add(user)
        await session.flush()
        return True