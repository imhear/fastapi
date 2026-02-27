from typing import Set, List
from app.modules.permission.repository import PermissionRepository
from app.domain.permission.interfaces import AbstractPermissionService


class PermissionService(AbstractPermissionService):
    def __init__(self, repository: PermissionRepository):
        self.repository = repository

    async def get_user_permissions(self, user_id: str) -> Set[str]:
        async with self.repository.transaction() as session:
            return await self.repository.get_user_permissions(session, user_id)

    async def check_user_permission(self, user_id: str, required_perm: str) -> bool:
        user_perms = await self.get_user_permissions(user_id)
        wildcards = self._generate_wildcards(required_perm)
        return any(perm in user_perms for perm in wildcards)

    def _generate_wildcards(self, required_perm: str) -> List[str]:
        parts = required_perm.split(':')
        wildcards = [required_perm]
        if len(parts) >= 2:
            wildcards.append(f"{parts[0]}:*")
        if len(parts) >= 3:
            wildcards.append(f"{parts[0]}:{parts[1]}:*")
        return wildcards