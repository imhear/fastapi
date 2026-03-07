# app/modules/role/repository.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List
from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.modules.role.models import SysRole, SysUserRole
from app.modules.role.schemas import RoleCreate, RoleUpdate

class RoleRepository:
    """角色仓储（只处理角色数据，无用户模块依赖）"""

    async def get_by_id(self, session: AsyncSession, role_id: str) -> Optional[SysRole]:
        """根据ID查角色"""
        # async with self._get_session(session) as s:
        stmt = select(SysRole).where(SysRole.id == role_id, SysRole.is_deleted == 0)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, session: AsyncSession) -> Optional[SysRole]:
        """根据CODE查角色"""
        # async with self._get_session(session) as s:
        stmt = select(SysRole).where(SysRole.code == code, SysRole.is_deleted == 0)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, session: AsyncSession, offset: int = 0, limit: int = 100) -> List[SysRole]:
        """查询所有未删除角色"""
        # async with self._get_session(session) as s:
        stmt = select(SysRole).where(SysRole.is_deleted == 0).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(self, role_in: RoleCreate, session: AsyncSession) -> SysRole:
        """创建角色"""
        role = SysRole(
            name=role_in.name,
            code=role_in.code,
            status=role_in.status,
        )
        session.add(role)
        await session.flush()
        # 思路1:简化管理，新建用户时角色为空，必须通过修改用户分配角色
        # 思路2:跨事务实现，用户模块实现创建用户，角色模块更新关联关系表，但这里有个问题，必须用户实例化后才有用户id
        # if role_in.permission_ids:
        #     # 分配权限（简化，实际需插入关联表）
        #     pass
        await session.refresh(role)
        return role

    async def update(self, role_id: str, role_update: RoleUpdate, session: AsyncSession) -> Optional[SysRole]:
        """更新角色"""
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
        """根据ID逻辑删除角色"""
        role = await self.get_by_id(role_id, session=session)
        if not role:
            return False
        role.is_deleted = 1
        session.add(role)
        await session.flush()
        return True

    async def assign_permissions(self, role_id: str, permission_ids: List[str], session: AsyncSession):
        """给角色分配权限"""
        stmt = delete(sys_role_permission).where(sys_role_permission.c.role_id == role_id)
        await session.execute(stmt)
        if permission_ids:
            values = [{"role_id": role_id, "permission_id": pid} for pid in permission_ids]
            stmt = insert(sys_role_permission).values(values)
            await session.execute(stmt)

    async def get_options(self, session: AsyncSession) -> List[SysRole]:
        """查询所有激活且未删除角色"""
        # async with self._get_session(session) as s:
        stmt = select(SysRole).where(SysRole.status == 1, SysRole.is_deleted == 0).order_by(SysRole.name)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_roles_by_user_id(self, session: AsyncSession, user_id: str):
        # async with self._get_session(session) as s:
        stmt = (
            select(SysRole)
            .join(SysUserRole, SysUserRole.role_id == SysRole.id)
            .where(SysUserRole.user_id == user_id, SysRole.status == 1, SysRole.is_deleted == 0)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def assign_roles_to_user(self, session: AsyncSession, user_id: str, role_ids: list[str]):
        """给用户分配角色（先删后加，原子操作）"""
        # 清空用户原有角色
        await session.execute(
            delete(SysUserRole).where(SysUserRole.user_id == user_id)
        )
        # 批量添加新角色
        if role_ids:
            session.add_all([
                SysUserRole(user_id=user_id, role_id=rid) for rid in role_ids
            ])
        await session.flush()  # 立即生效，不等待提交
