#
"""
用户API端点 - RPC风格URL重构
app/api/v1/endpoints/user.py
更新时间：2026/3/12

设计原则：
1. RPC风格URL设计，路径明确表达操作意图
2. 最小API逻辑：只处理HTTP相关逻辑
3. 依赖注入：通过依赖获取服务实例
4. 统一响应：所有接口返回标准格式
5. 错误处理：统一异常处理
"""
import json
from typing import Any, Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.composers.user_update_composer import UserUpdateComposer
from app.core.auth import CurrentUser
from app.core.database import get_async_db
from app.core.dataclasses import AuditContext
from app.core.log.service import LogService
from app.core.responses import ApiResponse, DataOutdated
from app.domain.user.interfaces import AbstractUserService
# from app.modules.audit.service import AuditService
# from app.modules.log.schemas import LogLevel
# from app.modules.log.service import LogService
from app.modules.user.models import User
from fastapi import APIRouter, Depends, HTTPException, Request, Path
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
from app.modules.user.schemas import UserCreate, UserResponse, UserProfileResponse, UserUpdate, ResetPasswordRequest
from app.modules.user.service import UserService
# from app.composers.user_detail import UserDetailComposer
from app.core.responses import ResourceNotFound, BadRequest

# 新增：导入审计日志装饰器和工具函数
from app.core.audit.utils import generate_operation_content
# from app.core.audit.decorator import with_audit_log

router = APIRouter(prefix="/users", tags=["users"])

UserServiceDep = Annotated[AbstractUserService, Depends(Provide[Container.user_service])]
# AuditServiceDep = Annotated[AuditService, Depends(Provide[Container.audit_service])]
DbDep = Annotated[AsyncSession, Depends(get_async_db)]
LogServiceDep = Annotated[LogService, Depends(Provide[Container.log_service])]
UserUpdateComposerDep = Annotated[UserUpdateComposer, Depends(Provide[Container.user_update_composer])]


# ========== 原有接口（无审计日志，保持不变） ==========
@router.get("/{user_id}/profile", response_model=UserProfileResponse)
@inject
async def get_user_profile(
    user_id: str,
    user_service: UserServiceDep,
):
    try:
        return await user_service.get_user_profile(user_id)
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=UserResponse)
@inject
async def create_user(
    user_in: UserCreate,
    current_user: CurrentUser,
    user_service: UserServiceDep,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        # TODO add current_user.id to UserCreate.create_user
        # TODO add current_user.id to UserCreate.update_user
        return await user_service.create_user(session=db,user_in=user_in)
    except BadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))

from app.core.audit.decorator import audit_log
# ========== 重构后接口（使用审计日志装饰器） ==========
@router.post(
    "/update/{id}",
    # response_model=ApiResponse[dict],
    summary="更新用户信息",
    description="更新用户信息并返回更新后的用户信息"
)
# @permission(
#     code=PermissionCode.USER_UPDATE.value,
#     name="用户更新权限",
#     description="需要【user:update】权限"
# )
@inject
@audit_log(
    module="user",
    operation_type="UPDATE",
    get_business_id=lambda **kwargs: str(kwargs['id']),
    get_operation_content=lambda **kwargs: {
        "operation": "更新用户信息",
        "changed_fields": [
            k for k in kwargs['user_update'].model_dump(exclude_unset=True).keys()
            if k not in ['version', 'role_ids']
        ],
        "version": str(getattr(kwargs['user_update'], 'version', ''))
    }
)
async def update_user(
        id: int,
        user_update: UserUpdate,
        request: Request,
        current_user: CurrentUser,
        composer: UserUpdateComposer = Depends(Provide[Container.user_update_composer]),
        # audit_service: AuditService = Depends(Provide[Container.audit_service]),
        db: AsyncSession = Depends(get_async_db),
        # _=Depends(permission_checker(PermissionCode.USER_UPDATE.value))
) -> Any:
    """更新用户信息"""
    # 此处只保留核心业务逻辑
    updated = await composer.update_user_with_roles(
        session=db,
        user_id=id,
        user_update=user_update,
        current_version=user_update.version,
        current_user_id=current_user.id
    )
    return ApiResponse.success(data=updated, msg="用户信息更新成功")


@router.post(
    "/reset-password/{id}",
    response_model=ApiResponse[dict],
    summary="重置用户密码",
    description="需要【user:update】权限，仅超级用户可访问"
)
# # @permission(
# #     code=PermissionCode.USER_UPDATE.value,
# #     name="用户更新权限",
# #     description="重置用户密码"
# # )
# @with_audit_log(reset_password_audit_config)  # 外层：审计日志装饰器
@inject                                       # 内层：依赖注入（必须）
@audit_log(
    module="user",
    operation_type="UPDATE",
    get_business_id=lambda **kwargs: str(kwargs['id']),
    get_operation_content=lambda **kwargs: {
        "operation": f"重置用户密码",
        "user_id": kwargs['id']
    }
)
async def reset_user_password(
        id: int,  # 路径参数
        req: ResetPasswordRequest,  # 修复：用Pydantic模型接收请求体
        request: Request,  # 新增：获取请求上下文
        current_user: CurrentUser,
        user_service: UserServiceDep,
        # audit_service: AuditServiceDep,  # 新增：注入审计服务
        db: DbDep,
) -> Any:
    """
    重置用户密码（仅业务逻辑+标准化透传审计上下文）
    """
    """重置用户密码"""
    result = await user_service.update_password(db, id, req.new_password)
    # return ApiResponse.success(data=result, msg="更新成功")
    # 修复：确保data返回字典类型，而不是字符串
    # 如果result是字符串"密码重置成功"，则包装成字典
    if isinstance(result, str):
        return ApiResponse.success(data={"message": result}, msg="密码重置成功")
    # 如果result是用户对象或其他数据，直接返回
    return ApiResponse.success(data={"user_id": id, "result": result}, msg="密码重置成功")

# ========== 待处理代码（过期代码） ==========
"""
@router.post(
    "/updateold/{id}",
    # response_model=ApiResponse[dict],
    summary="更新用户信息",
    description="更新用户信息并返回更新后的用户信息"
)
# @permission(
#     code=PermissionCode.USER_UPDATE.value,
#     name="用户更新权限",
#     description="需要【user:update】权限"
# )
@inject
async def update_user(
        id: str,
        user_update: UserUpdate,
        current_user: CurrentUser,
        # _superuser: CurrentSuperuser,
        user_service: UserServiceDep,
        # _=Depends(permission_checker(PermissionCode.USER_UPDATE.value))
) -> Any:
    更新用户信息
    try:
        print(f"🎯 API端点: 开始更新用户 {id}")
        print(f"📨 请求数据: {user_update.model_dump(exclude_unset=True)}")
        updated = await user_service.update_user(
            user_id=id,
            user_update=user_update,
            current_version=user_update.version,
            current_user_id=current_user.id  # 传递用户ID
        )
        # updated = await user_service.update_user(id, user_update, user_update.version)
        # response_data = UserResponse.model_validate(updated)
        print(f"🎯 API端点: 开始返回用户 {updated}")
        return ApiResponse.success(data=updated, msg="用户信息更新成功")
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户信息更新失败: {str(e)}")
"""

