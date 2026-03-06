<<<<<<< HEAD
from typing import List
=======
# app/modules/role/service.py
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

>>>>>>> develop
from app.modules.role.repository import RoleRepository
from app.modules.role.schemas import RoleCreate, RoleUpdate, RoleResponse
from app.services.redis_service import RedisService
from app.core.exceptions import ResourceNotFound, BadRequest
<<<<<<< HEAD


class RoleService:
=======
from app.domain.role.interfaces import AbstractRoleService

class RoleService(AbstractRoleService):  # 实现抽象接口
    """角色服务（只处理角色业务，无用户模块依赖）"""
>>>>>>> develop
    def __init__(self, role_repository: RoleRepository, redis_client):
        self.role_repository = role_repository
        self.redis_service = RedisService(redis_client)

    async def get_role_by_id(self, role_id: str) -> RoleResponse:
<<<<<<< HEAD
        async with self.role_repository.transaction() as session:
            role = await self.role_repository.get_by_id(role_id, session=session)
            if not role:
                raise ResourceNotFound("Role not found")
            return RoleResponse.model_validate(role)

    async def create_role(self, role_in: RoleCreate) -> RoleResponse:
=======
        """根据角色ID查角色（返回响应模型）"""
        role = await self.role_repository.get_by_id(role_id)
        if not role:
            raise ResourceNotFound("Role not found")
        return RoleResponse.model_validate(role)

    async def create_role(self, role_in: RoleCreate) -> RoleResponse:
        """创建角色（返回响应模型）"""
>>>>>>> develop
        async with self.role_repository.transaction() as session:
            existing = await self.role_repository.get_by_code(role_in.code, session=session)
            if existing:
                raise BadRequest("Role code already exists")
            role = await self.role_repository.create(role_in, session=session)
            return RoleResponse.model_validate(role)

    async def list_roles(self) -> List[RoleResponse]:
<<<<<<< HEAD
        async with self.role_repository.transaction() as session:
            roles = await self.role_repository.list_all(session=session)
            return [RoleResponse.model_validate(r) for r in roles]

    async def get_role_options(self) -> List[dict]:
        async with self.role_repository.transaction() as session:
            roles = await self.role_repository.get_options(session=session)
            return [{"value": str(r.id), "label": r.name, "tag": r.code} for r in roles]

    async def assign_permissions(self, role_id: str, permission_ids: List[str]):
=======
        """查询所有未删除角色"""
        roles = await self.role_repository.list_all()
        return [RoleResponse.model_validate(r) for r in roles]

    async def get_role_options(self) -> List[dict]:
        """查询所有激活且未删除角色"""
        roles = await self.role_repository.get_options()
        return [{"value": str(r.id), "label": r.name, "tag": r.code} for r in roles]

    async def assign_permissions(self, role_id: str, permission_ids: List[str]):
        """给角色分配权限"""
>>>>>>> develop
        async with self.role_repository.transaction() as session:
            role = await self.role_repository.get_by_id(role_id, session=session)
            if not role:
                raise ResourceNotFound("Role not found")
            await self.role_repository.assign_permissions(role_id, permission_ids, session)

    async def update_role(self, role_id: str, role_update: RoleUpdate) -> RoleResponse:
<<<<<<< HEAD
=======
        """更新角色"""
>>>>>>> develop
        async with self.role_repository.transaction() as session:
            role = await self.role_repository.update(role_id, role_update, session=session)
            if not role:
                raise ResourceNotFound("Role not found")
            return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: str):
<<<<<<< HEAD
        async with self.role_repository.transaction() as session:
            deleted = await self.role_repository.delete(role_id, session=session)
            if not deleted:
                raise ResourceNotFound("Role not found")
=======
        """根据ID逻辑删除角色"""
        async with self.role_repository.transaction() as session:
            deleted = await self.role_repository.delete(role_id, session=session)
            if not deleted:
                raise ResourceNotFound("Role not found")

    async def get_roles_by_user_id(
            self, user_id: str, session: AsyncSession | None = None
    ) -> list[RoleResponse]:
        """根据用户ID查角色（返回响应模型）"""
        roles = await self.role_repository.get_roles_by_user_id(user_id, session=session)
        return [RoleResponse.model_validate(r) for r in roles]

    async def assign_roles_to_user(
            self,
            user_id: str,
            role_ids: List[str],
            session: Optional[AsyncSession] = None  # 改为可选，统一范式
    ):
        """更新类方法：统一事务逻辑（兼容外部/内部事务）"""

        # 核心：提取业务逻辑到内部函数（和UserService一致）
        async def _assign(sess):
            # 1. 校验角色有效性（复用查询类方法的封装式写法）
            for rid in role_ids:
                role = await self.role_repository.get_by_id(rid, session=sess)
                if not role:
                    raise ResourceNotFound(f"角色ID {rid} 不存在")

            # 2. 执行角色分配（仓储层直传式写法）
            await self.role_repository.assign_roles_to_user(session=sess, user_id=user_id, role_ids=role_ids)

        # 3. 兼容外部/内部事务（和UserService完全一致）
        if session:
            await _assign(session)
        else:
            async with self.role_repository.transaction() as sess:
                await _assign(sess)

    # async def assign_roles_to_user(
    #         self, user_id: str, role_ids: list[str], session: AsyncSession | None = None
    # ) -> None:
    #     """给用户分配角色（校验角色是否存在）"""
    #     async with self.role_repository._get_session(session) as s:
    #         await self.role_repository.assign_roles_to_user(s, user_id, role_ids)
>>>>>>> develop
