# app/di/modules/role_container.py
from dependency_injector import containers, providers
from app.modules.role.repository import RoleRepository
from app.modules.role.service import RoleService
from app.domain.role.interfaces import AbstractRoleService


class RoleContainer(containers.DeclarativeContainer):
    async_session_factory = providers.Dependency()
    redis_client = providers.Dependency()

    role_repository = providers.Factory(
        RoleRepository,
        async_session_factory=async_session_factory,
    )

    # 绑定抽象接口 AbstractUserService 到具体实现 RoleService
    # role_service = providers.Factory(
    #     RoleService,
    #     repository=role_repository,
    #     redis_client=redis_client,
    # ).provides(AbstractRoleService)  # 绑定抽象接口

    # 不用抽象接口写法
    role_service = providers.Factory(
        RoleService,
        role_repository=role_repository,
        redis_client=redis_client,
    )
