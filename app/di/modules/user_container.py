# app/di/modules/user_container.py
from dependency_injector import containers, providers
from app.modules.user.repository import UserRepository
from app.modules.user.service import UserService
from app.domain.user.interfaces import AbstractUserService


class UserContainer(containers.DeclarativeContainer):
    async_session_factory = providers.Dependency()
    redis_client = providers.Dependency()

    user_repository = providers.Factory(
        UserRepository,
        async_session_factory=async_session_factory,
    )

    # 绑定抽象接口 AbstractUserService 到具体实现 UserService
    # user_service = providers.Factory(
    #     UserService,
    #     user_repository=user_repository,
    #     redis_client=redis_client,
    # ).provides(AbstractUserService)  # 关键：声明提供接口的实现

    # 不用抽象接口写法
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        redis_client=redis_client,
    )