# app/di/container.py
from dependency_injector import containers, providers
from dependency_injector.providers import Factory

from app.core.config import settings
from app.core.database import engine, AsyncSessionFactory, get_async_db
from app.core.redis import get_redis_client
from app.composers.user_detail import UserDetailComposer
from app.composers.user_update_composer import UserUpdateComposer
from app.domain.user.interfaces import AbstractUserService
from app.domain.user.repositories import AbstractUserRepository
from app.modules.auth.service import AuthService
from app.modules.log.service import LogService
from app.modules.permission.repository import PermissionRepository
from app.modules.permission.service import PermissionService
from app.modules.role.repository import RoleRepository
from app.modules.role.service import RoleService
from app.modules.user.repository import SQLAlchemyUserRepository
from app.modules.user.service import UserService
from app.services.captcha_service import CaptchaService
from app.services.redis_service import RedisService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.modules.user.api",
            "app.modules.role.api",
            "app.composers.user_detail",
            "app.utils.permission_checker",  # 新增，使 permission_checker 可被注入
            "app.core.auth",   # 新增
            "app.modules.auth.api",   # 新增
        ]
    )

    # 配置对象（单例）
    config = providers.Configuration()
    config.from_pydantic(settings)

    # Repo
    # 方式：用 Factory 直接创建实现类，且不传递任何参数（适配无 __init__ 的类）
    user_repo: AbstractUserRepository = Factory(SQLAlchemyUserRepository)  # 直接指定抽象类型
    role_repo = providers.Factory(RoleRepository)
    permission_repo = providers.Factory(PermissionRepository)

    # Service
    # 日志服务单例，确保处理器只启动一次
    log_service = providers.Singleton(LogService)

    # Redis 客户端资源
    redis_client = providers.Resource(get_redis_client)

    # Redis 服务（具体实现）
    redis_service = providers.Factory(
        RedisService,
        redis_client=redis_client,
    )
    # 验证码服务
    captcha_service = providers.Factory(
        CaptchaService,
        redis_service=redis_service,
    )
    user_service:AbstractUserService = Factory(
        UserService,
        repo=user_repo,
        redis_service=redis_service,
    )
    permission_service = providers.Factory(
        PermissionService,
        repo=permission_repo,
        redis_service=redis_service  # 新增：注入RedisService
    )
    auth_service = providers.Factory(
        AuthService,
        user_service=user_service,
        redis_service=redis_service  # 新增：注入RedisService
    )
    role_service = providers.Factory(
        RoleService,
        repo=role_repo,
        redis_service=redis_service  # 新增：注入RedisService
    )
    # dept_service = providers.Factory(
    #     DeptService,
    #     dept_repository=dept_repository,
    # )
    # # 字典服务
    # dict_service = providers.Factory(
    #     DictService,
    #     dict_repository=dict_repository,
    #     redis_service=redis_service
    # )

    # 聚合层 composer - 使用子容器的提供者属性，而不是 .provided
    user_detail_composer = providers.Factory(
        UserDetailComposer,
        user_service=user_service,  # 直接引用提供者
        role_service=role_service,  # 直接引用提供者
    )

    user_update_composer = providers.Factory(
        UserUpdateComposer,
        user_service=user_service,
        role_service=role_service,
    )