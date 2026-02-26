from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from app.di.container import Container
from app.modules.user.schemas import UserCreate, UserResponse, UserProfileResponse
from app.modules.user.service import UserService
from app.composers.user_detail import UserDetailComposer
from app.core.exceptions import ResourceNotFound, BadRequest

router = APIRouter(prefix="/users", tags=["users"])


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
        return await user_service.create_user(user_in)
    except BadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))

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