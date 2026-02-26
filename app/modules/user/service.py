# app/modules/user/service.py
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