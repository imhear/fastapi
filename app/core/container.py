"""
DI容器定义
app/core/container.py
"""
from dependency_injector import containers, providers
from dependency_injector.providers import Factory

from app.config.config import settings
from app.core.log.service import LogService
from app.domain.user.interfaces import AbstractUserService
from app.domain.user.repositories import AbstractUserRepository
from app.modules.audit.service import AuditService
from app.modules.auth.service import AuthService
from app.modules.user.repository import SQLAlchemyUserRepository
from app.modules.user.service import UserService
# 新增：导入UserUpdateComposer
from app.composers.user_update_composer import UserUpdateComposer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.user",
            "app.api.v1.endpoints.auth",
            # "app.composers.user_detail",
            # "app.utils.permission_checker",  # 新增，使 permission_checker 可被注入
            "app.core.auth",
            # "app.modules.auth.api",
        ]
    )

    # 配置对象（单例）
    config = providers.Configuration()
    config.from_pydantic(settings)

    # Repo
    # 方式：用 Factory 直接创建实现类，且不传递任何参数（适配无 __init__ 的类）
    user_repo: AbstractUserRepository = Factory(SQLAlchemyUserRepository)  # 直接指定抽象类型
    # role_repo = providers.Factory(RoleRepository)
    # permission_repo = providers.Factory(PermissionRepository)

    # Service
    # 日志服务（单例），确保处理器只启动一次
    log_service = providers.Singleton(LogService)
    # 审计服务（单例）
    audit_service = providers.Singleton(AuditService)

    # Redis 客户端资源
    # redis_client = providers.Resource(get_redis_client)

    # Redis 服务（具体实现）
    # redis_service = providers.Factory(
    #     RedisService,
    #     redis_client=redis_client,
    # )
    # 验证码服务
    # captcha_service = providers.Factory(
    #     CaptchaService,
    #     # redis_service=redis_service,
    # )
    user_service:AbstractUserService = Factory(
        UserService,
        repo=user_repo,
        # redis_service=redis_service,
    )
    # 新增：添加user_update_composer配置（解决核心报错）
    user_update_composer = providers.Factory(
        UserUpdateComposer,
        user_service=user_service,  # 注入用户服务依赖
        log_service=log_service,    # 注入日志服务依赖
    )

    # permission_service = providers.Factory(
    #     PermissionService,
    #     repo=permission_repo,
    #     # redis_service=redis_service
    # )
    auth_service = providers.Factory(
        AuthService,
        user_service=user_service,
        # redis_service=redis_service
    )
    # role_service = providers.Factory(
    #     RoleService,
    #     repo=role_repo,
    #     # redis_service=redis_service
    # )
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


# 创建容器实例并初始化
container = Container()
container.wire(modules=[
    "app.api.v1.endpoints.user",
    "app.api.v1.endpoints.auth",
    "app.core.middleware.log_middleware"],
)