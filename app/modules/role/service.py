# app/modules/role/service.py
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.role.repository import RoleRepository
from app.modules.role.schemas import RoleCreate, RoleUpdate, RoleResponse
from app.services.redis_service import RedisService
from app.core.exceptions import ResourceNotFound, BadRequest
from app.domain.role.interfaces import AbstractRoleService

class RoleService(AbstractRoleService):  # 实现抽象接口
    """角色服务（只处理角色业务，无用户模块依赖）"""
    def __init__(self, repo: RoleRepository, redis_service):
        self.role_repository = repo
        self.redis_service = redis_service

    async def get_role_by_id(self, session: AsyncSession, role_id: str) -> RoleResponse:
        """根据角色ID查角色（返回响应模型）"""
        role = await self.role_repository.get_by_id(session=session, role_id=role_id)
        if not role:
            raise ResourceNotFound("Role not found")
        return RoleResponse.model_validate(role)

    async def create_role(self, session: AsyncSession, role_in: RoleCreate) -> RoleResponse:
        """创建角色（返回响应模型）"""
        # async with self.role_repository.transaction() as session:
        existing = await self.role_repository.get_by_code(session=session, code=role_in.code)
        if existing:
            raise BadRequest("Role code already exists")
        role = await self.role_repository.create(session=session, role_in=role_in)
        return RoleResponse.model_validate(role)

    async def list_roles(self, session: AsyncSession) -> List[RoleResponse]:
        """查询所有未删除角色"""
        roles = await self.role_repository.list_all(session=session)
        return [RoleResponse.model_validate(r) for r in roles]

    async def get_role_options(self, session: AsyncSession) -> List[dict]:
        """查询所有激活且未删除角色"""
        roles = await self.role_repository.get_options(session=session)
        return [{"value": str(r.id), "label": r.name, "tag": r.code} for r in roles]

    async def assign_permissions(self, session: AsyncSession, role_id: str, permission_ids: List[str]):
        """给角色分配权限"""
        # async with self.role_repository.transaction() as session:
        role = await self.role_repository.get_by_id(session=session, role_id=role_id)
        if not role:
            raise ResourceNotFound("Role not found")
        await self.role_repository.assign_permissions(session=session, role_id=role_id, permission_ids=permission_ids)

    async def update_role(self, session: AsyncSession, role_id: str, role_update: RoleUpdate) -> RoleResponse:
        """更新角色"""
        # async with self.role_repository.transaction() as session:
        role = await self.role_repository.update(session=session, role_id=role_id, role_update=role_update)
        if not role:
            raise ResourceNotFound("Role not found")
        return RoleResponse.model_validate(role)

    async def delete_role(self, session: AsyncSession, role_id: str):
        """根据ID逻辑删除角色"""
        # async with self.role_repository.transaction() as session:
        deleted = await self.role_repository.delete(session=session, role_id=role_id)
        if not deleted:
            raise ResourceNotFound("Role not found")

    async def get_roles_by_user_id(
            self, session: AsyncSession, user_id: str
    ) -> list[RoleResponse]:
        """根据用户ID查角色（返回响应模型）"""
        roles = await self.role_repository.get_roles_by_user_id(session=session, user_id=user_id)
        return [RoleResponse.model_validate(r) for r in roles]

    async def assign_roles_to_user(
            self,
            session: AsyncSession,
            user_id: str,
            role_ids: List[str]
    ):
        """更新类方法：统一事务逻辑（兼容外部/内部事务）"""
        # 核心：提取业务逻辑到内部函数（和UserService一致）
        # async def _assign(sess):
        # 1. 校验角色有效性（复用查询类方法的封装式写法）
        for role_id in role_ids:
            role = await self.role_repository.get_by_id(session=session, role_id=role_id)
            if not role:
                raise ResourceNotFound(f"角色ID {role_id} 不存在")

        # 2. 执行角色分配（仓储层直传式写法）
        await self.role_repository.assign_roles_to_user(session=session, user_id=user_id, role_ids=role_ids)