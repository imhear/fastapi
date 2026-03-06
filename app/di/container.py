# app/di/container.py
from dependency_injector import containers, providers

<<<<<<< HEAD
from app.composers.user_detail import UserDetailComposer
=======

>>>>>>> develop
from app.core.config import settings
from app.core.database import engine, AsyncSessionFactory, get_async_db
from app.core.redis import get_redis_client
from app.di.modules.user_container import UserContainer
from app.di.modules.role_container import RoleContainer
<<<<<<< HEAD
=======
from app.di.modules.permission_container import PermissionContainer
from app.di.modules.auth_container import AuthContainer
from app.composers.user_detail import UserDetailComposer
from app.composers.user_update_composer import UserUpdateComposer
from app.modules.log.service import LogService
from app.services.captcha_service import CaptchaService
from app.services.redis_service import RedisService
>>>>>>> develop


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.modules.user.api",
            "app.modules.role.api",
            "app.composers.user_detail",
<<<<<<< HEAD
=======
            "app.utils.permission_checker",  # 新增，使 permission_checker 可被注入
            "app.core.auth",   # 新增
            "app.modules.auth.api",   # 新增
>>>>>>> develop
        ]
    )

    # 配置对象（单例）
    config = providers.Configuration()
    config.from_pydantic(settings)

    # 核心资源（单例）
    async_session_factory = providers.Singleton(lambda: AsyncSessionFactory)

    # 请求级会话资源（由 get_async_db 提供）
    async_db = providers.Resource(get_async_db)

<<<<<<< HEAD
    # Redis 客户端资源
    redis_client = providers.Resource(get_redis_client)

=======
    # 日志服务单例，确保处理器只启动一次
    log_service = providers.Singleton(LogService)

    # Redis 客户端资源
    redis_client = providers.Resource(get_redis_client)

    # Redis 服务（具体实现）
    redis_service = providers.Factory(
        RedisService,
        redis_client=redis_client,
    )

>>>>>>> develop
    # 子容器：用户模块
    user_container = providers.Container(
        UserContainer,
        async_session_factory=async_session_factory,
        redis_client=redis_client,
    )

<<<<<<< HEAD
=======
    # 验证码服务
    captcha_service = providers.Factory(
        CaptchaService,
        redis_service=redis_service,
    )

>>>>>>> develop
    # 子容器：角色模块
    role_container = providers.Container(
        RoleContainer,
        async_session_factory=async_session_factory,
        redis_client=redis_client,
    )

<<<<<<< HEAD
=======
    # 子容器：权限模块
    permission_container = providers.Container(
        PermissionContainer,
        async_session_factory=async_session_factory,
    )

    # 认证子容器
    auth_container = providers.Container(
        AuthContainer,
        user_service=user_container.user_service,      # 注入 UserService
        redis_service=redis_service,                   # 注入 RedisService
    )

>>>>>>> develop
    # 聚合层 composer - 使用子容器的提供者属性，而不是 .provided
    user_detail_composer = providers.Factory(
        UserDetailComposer,
        user_service=user_container.user_service,  # 直接引用提供者
        role_service=role_container.role_service,  # 直接引用提供者
<<<<<<< HEAD
=======
    )

    user_update_composer = providers.Factory(
        UserUpdateComposer,
        user_service=user_container.user_service,
        role_service=role_container.role_service,
        async_session_factory=async_session_factory,   # 直接从父容器注入
>>>>>>> develop
    )