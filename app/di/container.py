# app/di/container.py
from dependency_injector import containers, providers

from app.composers.user_detail import UserDetailComposer
from app.core.config import settings
from app.core.database import engine, AsyncSessionFactory, get_async_db
from app.core.redis import get_redis_client
from app.di.modules.user_container import UserContainer
from app.di.modules.role_container import RoleContainer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.modules.user.api",
            "app.modules.role.api",
            "app.composers.user_detail",
        ]
    )

    # 配置对象（单例）
    config = providers.Configuration()
    config.from_pydantic(settings)

    # 核心资源（单例）
    async_session_factory = providers.Singleton(lambda: AsyncSessionFactory)

    # 请求级会话资源（由 get_async_db 提供）
    async_db = providers.Resource(get_async_db)

    # Redis 客户端资源
    redis_client = providers.Resource(get_redis_client)

    # 子容器：用户模块
    user_container = providers.Container(
        UserContainer,
        async_session_factory=async_session_factory,
        redis_client=redis_client,
    )

    # 子容器：角色模块
    role_container = providers.Container(
        RoleContainer,
        async_session_factory=async_session_factory,
        redis_client=redis_client,
    )

    # 聚合层 composer - 使用子容器的提供者属性，而不是 .provided
    user_detail_composer = providers.Factory(
        UserDetailComposer,
        user_service=user_container.user_service,  # 直接引用提供者
        role_service=role_container.role_service,  # 直接引用提供者
    )