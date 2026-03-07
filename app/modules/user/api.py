# app/modules/user/api.py

from typing import Any, Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.composers.user_update_composer import UserUpdateComposer
from app.core.auth import CurrentUser
from app.core.database import get_async_db
from app.core.responses import ApiResponse
from app.models.base import datetime_encoder
from app.modules.log.schemas import LogLevel
from app.modules.log.service import LogService
from app.modules.user.models import SysUser
from fastapi import APIRouter, Depends, HTTPException, Request
from dependency_injector.wiring import inject, Provide
from app.di.container import Container
from app.modules.user.schemas import UserCreate, UserResponse, UserProfileResponse, UserUpdate
from app.modules.user.service import UserService
from app.composers.user_detail import UserDetailComposer
from app.core.exceptions import ResourceNotFound, BadRequest

router = APIRouter(prefix="/users", tags=["users"])

UserServiceDep = Annotated[UserService, Depends(Provide[Container.user_service])]

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
@inject
async def get_user_profile(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
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
    user_service: UserService = Depends(Provide[Container.user_service]),
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
        id: str,
        user_update: UserUpdate,
        request: Request,
        current_user: CurrentUser,
        composer: UserUpdateComposer = Depends(Provide[Container.user_update_composer]),
        log_service: LogService = Depends(Provide[Container.log_service]),
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
        updated = await composer.update_user_with_roles(
            session=db,
            user_id=id,
            user_update=user_update,
            current_version=user_update.version,
            current_user_id=current_user.id  # 传递用户ID
        )
        # 记录审计级日志
        await log_service.log(
            operation_type="UPDATE",
            module="user",
            operator_id=current_user.id,
            operator_name=current_user.username,
            content={"user_id": id, "updates": user_update.model_dump(exclude_unset=True)},
            level=LogLevel.AUDIT,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            request_id=request_id,
            api_path=api_path,
            http_method=http_method,
        )
        return ApiResponse.success(data=updated, msg="用户信息更新成功")
    # except ResourceNotFound as e:
    #     raise HTTPException(status_code=404, detail=str(e))
    # except BadRequest as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 记录错误级日志
        await log_service.log(
            operation_type="UPDATE",
            module="user",
            operator_id=current_user.id,
            operator_name=current_user.username,
            content={"user_id": id},
            result="FAILURE",
            error_detail=str(e),
            level=LogLevel.ERROR,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            request_id=request_id,
            api_path=api_path,
            http_method=http_method,
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


@router.get("/{user_id}/detail")
@inject
async def get_user_detail(
    user_id: str,
    composer: UserDetailComposer = Depends(Provide[Container.user_detail_composer]),
    db: AsyncSession = Depends(get_async_db),
):
    """获取用户详细信息（包含角色）"""
    try:
        result = await composer.compose(session=db,user_id=user_id)
        return result
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))