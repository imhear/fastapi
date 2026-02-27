from dependency_injector import containers, providers
from app.modules.permission.repository import PermissionRepository
from app.modules.permission.service import PermissionService
from app.domain.permission.interfaces import AbstractPermissionService


class PermissionContainer(containers.DeclarativeContainer):
    async_session_factory = providers.Dependency()

    permission_repository = providers.Factory(
        PermissionRepository,
    )

    permission_service = providers.Factory(
        PermissionService,
        repository=permission_repository,
    )