from typing import List
from app.modules.role.repository import RoleRepository
from app.modules.role.schemas import RoleCreate, RoleUpdate, RoleResponse
from app.services.redis_service import RedisService
from app.core.exceptions import ResourceNotFound, BadRequest


class RoleService:
    def __init__(self, role_repository: RoleRepository, redis_client):
        self.role_repository = role_repository
        self.redis_service = RedisService(redis_client)

    async def get_role_by_id(self, role_id: str) -> RoleResponse:
        async with self.role_repository.transaction() as session:
            role = await self.role_repository.get_by_id(role_id, session=session)
            if not role:
                raise ResourceNotFound("Role not found")
            return RoleResponse.model_validate(role)

    async def create_role(self, role_in: RoleCreate) -> RoleResponse:
        async with self.role_repository.transaction() as session:
            existing = await self.role_repository.get_by_code(role_in.code, session=session)
            if existing:
                raise BadRequest("Role code already exists")
            role = await self.role_repository.create(role_in, session=session)
            return RoleResponse.model_validate(role)

    async def list_roles(self) -> List[RoleResponse]:
        async with self.role_repository.transaction() as session:
            roles = await self.role_repository.list_all(session=session)
            return [RoleResponse.model_validate(r) for r in roles]

    async def get_role_options(self) -> List[dict]:
        async with self.role_repository.transaction() as session:
            roles = await self.role_repository.get_options(session=session)
            return [{"value": str(r.id), "label": r.name, "tag": r.code} for r in roles]

    async def assign_permissions(self, role_id: str, permission_ids: List[str]):
        async with self.role_repository.transaction() as session:
            role = await self.role_repository.get_by_id(role_id, session=session)
            if not role:
                raise ResourceNotFound("Role not found")
            await self.role_repository.assign_permissions(role_id, permission_ids, session)

    async def update_role(self, role_id: str, role_update: RoleUpdate) -> RoleResponse:
        async with self.role_repository.transaction() as session:
            role = await self.role_repository.update(role_id, role_update, session=session)
            if not role:
                raise ResourceNotFound("Role not found")
            return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: str):
        async with self.role_repository.transaction() as session:
            deleted = await self.role_repository.delete(role_id, session=session)
            if not deleted:
                raise ResourceNotFound("Role not found")