# app/modules/user/service.py
from typing import Dict, Any

from app.modules.user.repository import UserRepository
from app.modules.user.schemas import UserCreate, UserUpdate, UserResponse, UserProfileResponse
from app.services.redis_service import RedisService
from app.core.exceptions import ResourceNotFound, BadRequest
from app.domain.user.interfaces import AbstractUserService


class UserService(AbstractUserService):  # 实现抽象接口
    def __init__(self, user_repository: UserRepository, redis_client):
        self.user_repository = user_repository
        self.redis_service = RedisService(redis_client)

    async def get_user_by_id(self, user_id: str):
        async with self.user_repository.transaction() as session:
            user = await self.user_repository.get_by_id(user_id, session=session)
            if not user:
                raise ResourceNotFound("User not found")
            return user

    async def get_user_by_username(self, username: str):
        async with self.user_repository.transaction() as session:
            user = await self.user_repository.get_by_username(username, session=session)
            if not user:
                raise ResourceNotFound("User not found")
            return user

    async def get_user_profile(self, user_id: str) -> UserProfileResponse:
        user = await self.get_user_by_id(user_id)
        # 此处可通过其他服务获取角色名称，为简化暂留空
        return UserProfileResponse(
            id=str(user.id),
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            roles=[],
        )

    async def create_user(self, user_in: UserCreate) -> UserResponse:
        async with self.user_repository.transaction() as session:
            existing = await self.user_repository.get_by_username(user_in.username, session=session)
            if existing:
                raise BadRequest("Username already exists")
            # 密码加密（略）
            user = await self.user_repository.create(user_in, session=session)
            return UserResponse.model_validate(user)


    async def update_user(self, user_id: str, user_update: UserUpdate, current_version: int) -> Dict[str, Any]:
        """
        更新用户信息（返回前端格式）

        Args:
            user_id: 用户ID
            user_update: 更新数据
            current_version: 乐观锁版本号

        Returns:
            前端格式的更新后用户信息
        """
        print(f"🎯 service.update_user: 开始")
        # 1. 获取用户
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFound("User not found")
        # 检查版本号
        if user.version != current_version:
            raise BadRequest("数据已被其他用户修改，请刷新后重试")

        # 2. 邮箱唯一性验证（如果修改邮箱）
        # if user_update.email and user_update.email != user.email:
        #     existing_user = await self.user_repository.get_by_email(email=user_update.email)
        #     if existing_user:
        #         raise BadRequest(detail=f"邮箱 '{user_update.email}' 已被使用")

        async with self.user_repository.transaction() as session:
            # 3. 提取更新数据
            print(f"🎯 service.update_user: 开始提取更新数据")
            update_data = user_update.model_dump(exclude_unset=True)
            print(f"🎯 service.update_user: 结束提取更新数据")

            # 5. 更新基础字段
            for key, value in update_data.items():
                if key not in ["role_ids"]:
                    setattr(user, key, value)

            # 版本号递增
            user.version += 1
            # 设置最后更新人
            # user.updated_by = current_user_id

            # 6. 更新角色（如果有）
            # if "role_ids" in update_data:
            #     await self.user_repository.assign_roles(
            #         user_id=user_id,
            #         role_ids=update_data["role_ids"],
            #         session=session
            #     )

            # 7. 保存更新
            await self.user_repository.update(user_id=user.id ,user_update=user, session=session)

            # 8. 重新加载完整数据
            updated_user = await self.get_user_by_id(user_id)

            # 9. 转换为前端格式返回 TODO 待实现格式转换
            # return user_mapper.to_user_detail(updated_user)
            return updated_user
