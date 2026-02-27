# app/di/modules/auth_container.py

from dependency_injector import containers, providers

from app.domain.redis.interfaces import AbstractRedisService
from app.domain.user.interfaces import AbstractUserService
from app.modules.auth.service import AuthService
from app.domain.auth.interfaces import AbstractAuthService


class AuthContainer(containers.DeclarativeContainer):
    user_service = providers.Dependency(instance_of=AbstractUserService)
    redis_service = providers.Dependency(instance_of=AbstractRedisService)

    auth_service = providers.Factory(
        AuthService,
        user_service=user_service,
        redis_service=redis_service,
    )