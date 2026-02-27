from typing import List, Set, Optional
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.permission.models import SysPermission
from app.modules.role.models import SysRole, sys_role_permission
from app.modules.user.models import SysUser, sys_user_role


class PermissionRepository:
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
        """查询用户拥有的所有权限代码（去重）"""
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
                SysRole.is_active == True,
                SysPermission.is_deleted == 0,
                SysPermission.is_active == True,
            )
        )
        result = await db.execute(stmt)
        return {row[0] for row in result.all()}