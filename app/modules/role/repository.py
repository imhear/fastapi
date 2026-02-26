from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List
from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.modules.role.models import SysRole, sys_role_permission
from app.modules.role.schemas import RoleCreate, RoleUpdate


class RoleRepository:
    def __init__(self, async_session_factory: async_sessionmaker):
        self._async_session_factory = async_session_factory

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._async_session_factory() as session:
            async with session.begin():
                yield session

    # async def _get_session(self, session: Optional[AsyncSession] = None) -> AsyncGenerator[AsyncSession, None]:
    #     if session is not None:
    #         yield session
    #     else:
    #         async with self._async_session_factory() as new_session:
    #             yield new_session

    @asynccontextmanager
    async def _get_session(self, session: Optional[AsyncSession] = None) -> AsyncGenerator[AsyncSession, None]:
        if session is not None:
            yield session
        else:
            async with self._async_session_factory() as new_session:
                yield new_session

    async def get_by_id(self, role_id: str, session: Optional[AsyncSession] = None) -> Optional[SysRole]:
        async with self._get_session(session) as s:
            stmt = select(SysRole).where(SysRole.id == role_id, SysRole.is_deleted == 0)
            result = await s.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_code(self, code: str, session: Optional[AsyncSession] = None) -> Optional[SysRole]:
        async with self._get_session(session) as s:
            stmt = select(SysRole).where(SysRole.code == code, SysRole.is_deleted == 0)
            result = await s.execute(stmt)
            return result.scalar_one_or_none()

    async def list_all(self, offset: int = 0, limit: int = 100, session: Optional[AsyncSession] = None) -> List[SysRole]:
        async with self._get_session(session) as s:
            stmt = select(SysRole).where(SysRole.is_deleted == 0).offset(offset).limit(limit)
            result = await s.execute(stmt)
            return result.scalars().all()

    async def create(self, role_in: RoleCreate, session: AsyncSession) -> SysRole:
        role = SysRole(
            name=role_in.name,
            code=role_in.code,
            status=role_in.status,
        )
        session.add(role)
        await session.flush()
        if role_in.permission_ids:
            # 分配权限（简化，实际需插入关联表）
            pass
        await session.refresh(role)
        return role

    async def update(self, role_id: str, role_update: RoleUpdate, session: AsyncSession) -> Optional[SysRole]:
        role = await self.get_by_id(role_id, session=session)
        if not role:
            return None
        update_data = role_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key != "permission_ids":
                setattr(role, key, value)
        if "permission_ids" in update_data:
            await self.assign_permissions(role_id, update_data["permission_ids"], session)
        session.add(role)
        await session.flush()
        await session.refresh(role)
        return role

    async def delete(self, role_id: str, session: AsyncSession) -> bool:
        role = await self.get_by_id(role_id, session=session)
        if not role:
            return False
        role.is_deleted = 1
        session.add(role)
        await session.flush()
        return True

    async def assign_permissions(self, role_id: str, permission_ids: List[str], session: AsyncSession):
        stmt = delete(sys_role_permission).where(sys_role_permission.c.role_id == role_id)
        await session.execute(stmt)
        if permission_ids:
            values = [{"role_id": role_id, "permission_id": pid} for pid in permission_ids]
            stmt = insert(sys_role_permission).values(values)
            await session.execute(stmt)

    async def get_options(self, session: Optional[AsyncSession] = None) -> List[SysRole]:
        async with self._get_session(session) as s:
            stmt = select(SysRole).where(SysRole.status == 1, SysRole.is_deleted == 0).order_by(SysRole.name)
            result = await s.execute(stmt)
            return result.scalars().all()