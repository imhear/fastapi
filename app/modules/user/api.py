from typing import Any, Annotated

from app.core.auth import CurrentUser
from app.core.responses import ApiResponse
from app.models.base import datetime_encoder
from app.modules.user.models import SysUser
from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from app.di.container import Container
from app.modules.user.schemas import UserCreate, UserResponse, UserProfileResponse, UserUpdate
from app.modules.user.service import UserService
from app.composers.user_detail import UserDetailComposer
from app.core.exceptions import ResourceNotFound, BadRequest

router = APIRouter(prefix="/users", tags=["users"])

UserServiceDep = Annotated[UserService, Depends(Provide[Container.user_container.user_service])]

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
@inject
async def get_user_profile(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_container.user_service]),
):
    try:
        return await user_service.get_user_profile(user_id)
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=UserResponse)
@inject
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(Provide[Container.user_container.user_service]),
):
    try:
        # TODO add current_user.id to UserCreate.create_user
        # TODO add current_user.id to UserCreate.update_user
        return await user_service.create_user(user_in)
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
):
    """获取用户详细信息（包含角色）"""
    try:
        result = await composer.compose(user_id)
        return result
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))