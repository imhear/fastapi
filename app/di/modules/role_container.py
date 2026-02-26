# app/di/modules/role_container.py
from dependency_injector import containers, providers
from app.modules.role.repository import RoleRepository
from app.modules.role.service import RoleService


class RoleContainer(containers.DeclarativeContainer):
    async_session_factory = providers.Dependency()
    redis_client = providers.Dependency()

    role_repository = providers.Factory(
        RoleRepository,
        async_session_factory=async_session_factory,
    )

    role_service = providers.Factory(
        RoleService,
        role_repository=role_repository,
        redis_client=redis_client,
    )