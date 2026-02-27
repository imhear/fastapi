# app/di/modules/permission_container.py
from dependency_injector import containers, providers
from app.modules.permission.repository import PermissionRepository
from app.modules.permission.service import PermissionService


class PermissionContainer(containers.DeclarativeContainer):
    async_session_factory = providers.Dependency()

    permission_repository = providers.Factory(
        PermissionRepository,
        async_session_factory=async_session_factory,
    )

    permission_service = providers.Factory(
        PermissionService,
        repository=permission_repository,
    )