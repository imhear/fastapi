# app/di/modules/user_container.py
from dependency_injector import containers, providers
from app.modules.user.repository import UserRepository
from app.modules.user.service import UserService


class UserContainer(containers.DeclarativeContainer):
    async_session_factory = providers.Dependency()
    redis_client = providers.Dependency()

    user_repository = providers.Factory(
        UserRepository,
        async_session_factory=async_session_factory,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        redis_client=redis_client,
    )