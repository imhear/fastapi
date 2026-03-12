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
from app.core.log.service import LogService
from app.core.responses import ApiResponse
from app.domain.user.interfaces import AbstractUserService
from app.modules.audit.service import AuditService
# from app.modules.log.schemas import LogLevel
# from app.modules.log.service import LogService
from app.modules.user.models import User
from fastapi import APIRouter, Depends, HTTPException, Request, Path
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
from app.modules.user.schemas import UserCreate, UserResponse, UserProfileResponse, UserUpdate
from app.modules.user.service import UserService
# from app.composers.user_detail import UserDetailComposer
from app.core.responses import ResourceNotFound, BadRequest

router = APIRouter(prefix="/users", tags=["users"])

UserServiceDep = Annotated[AbstractUserService, Depends(Provide[Container.user_service])]

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
async def update_user(
        id: int,
        user_update: UserUpdate,
        request: Request,
        current_user: CurrentUser,
        composer: UserUpdateComposer = Depends(Provide[Container.user_update_composer]),
        log_service: LogService = Depends(Provide[Container.log_service]),
        audit_service: AuditService = Depends(Provide[Container.audit_service]),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    更新用户信息
    """
    try:
        print(f"🎯 API端点: 开始更新用户 {id}")
        print(f"📨 请求数据: {user_update.model_dump(exclude_unset=True)}")
        """原子更新用户信息及角色（使用组合器）"""
        # 获取全局request_id和API信息
        request_id = request.state.request_id
        api_path = str(request.url.path)
        http_method = request.method
        ip_address = request.client.host
        updated = await composer.update_user_with_roles(
            session=db,
            user_id=id,
            user_update=user_update,
            current_version=user_update.version,
            current_user_id=current_user.id  # 传递用户ID
        )
        # 记录审计日志
        operation_content_dict = {"user_id": id, "updates": user_update.model_dump(exclude_unset=True)}
        # 常用参数：
        # ensure_ascii = False：避免将非ASCII字符转义为 \u序列。
        # indent = 2：格式化输出（多行缩进），便于阅读，但会增加日志体积。
        # default = str：处理不可序列化的类型（如datetime），将其转为字符串。
        operation_content_str = json.dumps(operation_content_dict, ensure_ascii=False)

        await audit_service.record_audit_log(
            db=db,
            operator_id=current_user.id,
            operator_name=current_user.username,
            module="user",
            operation_type="UPDATE",
            business_id=str(id),
            operation_content=operation_content_str,
            operation_result="SUCCESS",
            error_msg=None,
            ip_address=ip_address,
            request_id=request_id,
            )

        return ApiResponse.success(data=updated, msg="用户信息更新成功")
    # except ResourceNotFound as e:
    #     raise HTTPException(status_code=404, detail=str(e))
    # except BadRequest as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 记录错误级日志
        await audit_service.record_audit_log(
            db=db,
            operator_id=current_user.id,
            operator_name=current_user.username,
            module="user",
            operation_type="UPDATE",
            business_id=str(id),
            operation_content=operation_content_str,
            operation_result="FAILURE",
            error_msg=None,
            ip_address=ip_address,
            request_id=request_id,
            )
        raise HTTPException(status_code=500, detail=f"用户信息更新失败: {str(e)}")



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
    """
    更新用户信息
    """
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


# @router.get("/{user_id}/detail")
# @inject
# async def get_user_detail(
#     user_id: str,
#     composer: UserDetailComposer = Depends(Provide[Container.user_detail_composer]),
#     db: AsyncSession = Depends(get_async_db),
# ):
#     """获取用户详细信息（包含角色）"""
#     try:
#         result = await composer.compose(session=db,user_id=user_id)
#         return result
#     except ResourceNotFound as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/reset-password/{id}",
    # response_model=Message,
    summary="重置用户密码",
    description="需要【user:update】权限，仅超级用户可访问"
)
# @permission(
#     code=PermissionCode.USER_UPDATE.value,
#     name="用户更新权限",
#     description="重置用户密码"
# )
@inject
async def reset_user_password(
    id: int,  # 路径参数
    new_password: str,  # 请求体
    current_user: CurrentUser,
    # _superuser: CurrentSuperuser,  # 无默认值
    user_service: UserServiceDep,  # 无默认值
    # _ = Depends(permission_checker(PermissionCode.USER_UPDATE.value))  # 有默认值
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    return await user_service.update_password(db, id, new_password)
