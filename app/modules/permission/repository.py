# app/modules/permission/repository.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Set, Optional
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.modules.permission.models import SysPermission
from app.modules.role.models import SysRole, sys_role_permission
from app.modules.user.models import SysUser, sys_user_role


class PermissionRepository:
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

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[SysPermission]:
        stmt = select(SysPermission).where(SysPermission.code == code, SysPermission.is_deleted == 0)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, perm_id: str) -> Optional[SysPermission]:
        stmt = select(SysPermission).where(SysPermission.id == perm_id, SysPermission.is_deleted == 0)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, db: AsyncSession, offset: int = 0, limit: int = 100) -> List[SysPermission]:
        stmt = select(SysPermission).where(SysPermission.is_deleted == 0).offset(offset).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_user_permissions(self, db: AsyncSession, user_id: str) -> Set[str]:
        stmt = (
            select(distinct(SysPermission.code))
            .join(sys_role_permission, SysPermission.id == sys_role_permission.c.permission_id)
            .join(SysRole, sys_role_permission.c.role_id == SysRole.id)
            .join(sys_user_role, SysRole.id == sys_user_role.c.role_id)
            .join(SysUser, sys_user_role.c.user_id == SysUser.id)
            .where(
                SysUser.id == user_id,
                SysUser.is_deleted == 0,
                SysRole.is_deleted == 0,
                SysRole.status == 1,
                SysPermission.is_deleted == 0,
                SysPermission.status == 1,
            )
        )
        result = await db.execute(stmt)
        return {row[0] for row in result.all()}