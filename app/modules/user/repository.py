# app/modules/user/repository.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.modules.user.models import SysUser
from app.modules.user.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, async_session_factory: async_sessionmaker):
        self._async_session_factory = async_session_factory

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._async_session_factory() as session:
            async with session.begin():
                yield session

    @asynccontextmanager
    async def _get_session(self, session: Optional[AsyncSession] = None) -> AsyncGenerator[AsyncSession, None]:
        if session is not None:
            yield session
        else:
            async with self._async_session_factory() as new_session:
                yield new_session

    async def get_by_id(self, user_id: str, session: Optional[AsyncSession] = None) -> Optional[SysUser]:
        async with self._get_session(session) as s:
            stmt = select(SysUser).where(SysUser.id == user_id, SysUser.is_deleted == 0)
            result = await s.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_username(self, username: str, session: Optional[AsyncSession] = None) -> Optional[SysUser]:
        async with self._get_session(session) as s:
            stmt = select(SysUser).where(SysUser.username == username, SysUser.is_deleted == 0)
            result = await s.execute(stmt)
            return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate, session: AsyncSession) -> SysUser:
        user = SysUser(
            username=user_in.username,
            nickname=user_in.nickname,
            email=user_in.email,
            password=user_in.password,  # 密码加密应在服务层完成
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def update(self, user_id: str, user_update: SysUser, session: AsyncSession) -> Optional[SysUser]:
        print(f"🎯 repository.update_user: 开始1")
        # user = await self.get_by_id(user_id, session=session)
        print(f"🎯 repository.update_user: 开始2")
        # if not user:
        #     return None
        print(f"🎯 repository.update_user: 开始提取更新数据")
        # update_data = user_update.model_dump(exclude_unset=True)
        print(f"🎯 repository.update_user: 结束提取更新数据")
        # update_data = user_update.model_dump(exclude_unset=True)
        # for key, value in update_data.items():
        #     setattr(user, key, value)
        # session.add(user)
        session.add(user_update)
        await session.flush()
        await session.refresh(user_update)
        return user_update

    async def delete(self, user_id: str, session: AsyncSession) -> bool:
        user = await self.get_by_id(user_id, session=session)
        if not user:
            return False
        user.is_deleted = 1
        session.add(user)
        await session.flush()
        return True