# app/modules/user/service.py
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.repositories import AbstractUserRepository
from app.modules.user.models import SysUser
from app.modules.user.schemas import UserCreate, UserUpdate, UserResponse, UserProfileResponse
from app.services.redis_service import RedisService
from app.core.exceptions import ResourceNotFound, BadRequest
from app.domain.user.interfaces import AbstractUserService


class UserService(AbstractUserService):  # 实现抽象接口
    def __init__(self, repo: AbstractUserRepository, redis_service):
        self.user_repository = repo
        self.redis_service = redis_service

    async def get_user_by_id(self, session: AsyncSession, user_id: str):
        user = await self.user_repository.get_by_id(session=session, user_id=user_id)
        if not user:
            raise ResourceNotFound("User not found")
        return user

    async def get_user_by_username(self, session: AsyncSession, username: str):
        user = await self.user_repository.get_by_username(session=session, username=username)
        if not user:
            raise ResourceNotFound("User not found")
        return user

    async def get_user_profile(self, session: AsyncSession, user_id: str) -> UserProfileResponse:
        user = await self.get_user_by_id(session=session, user_id=user_id)
        # 此处可通过其他服务获取角色名称，为简化暂留空
        return UserProfileResponse(
            id=str(user.id),
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            roles=[],
        )

    async def create_user(self, session: AsyncSession, user_in: UserCreate) -> UserResponse:
        existing = await self.user_repository.get_by_username(session=session, username=user_in.username)
        if existing:
            raise BadRequest("Username already exists")
        # 密码加密（略）
        user = await self.user_repository.create(session=session, user_in=user_in)
        return UserResponse.model_validate(user)

    async def update_user(self, session: AsyncSession, user_id: str, user_update: UserUpdate, current_version: int, current_user_id: str) -> UserResponse:
        print(f"🎯 service.update_user: 开始，操作人ID: {current_user_id}")
        user = await self.get_user_by_id(session=session, user_id=user_id)
        if not user:
            raise ResourceNotFound("User not found")

        # 操作人ID检查
        if current_user_id is None:
            raise BadRequest("缺少操作人ID")

        # 乐观锁检查
        if current_version is None:
            raise BadRequest("缺少乐观锁版本号")
        # TODO 方便测试，需要解除注释
        if user.version != current_version:
            raise BadRequest("数据已被其他用户修改，请刷新后重试")

        # 提取更新数据，排除版本号和关联字段
        update_data = user_update.model_dump(exclude_unset=True, exclude={'version', 'role_ids'})

        # 只更新模型存在的字段
        model_columns = {c.name for c in SysUser.__table__.columns}
        valid_update_data = {k: v for k, v in update_data.items() if k in model_columns}

        for key, value in valid_update_data.items():
            setattr(user, key, value)

        # 设置更新人ID
        user.update_by = current_user_id  # 关键赋值

        # 版本号递增（不依赖前端传入的 version）
        user.version += 1

        # 保存
        updated = await self.user_repository.update(session=session, obj=user)
        return UserResponse.model_validate(updated)
