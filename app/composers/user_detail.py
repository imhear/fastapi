# app/composers/user_detail.py
from app.modules.role.schemas import RoleResponse
from app.modules.user.schemas import UserResponse
from app.modules.user.service import UserService
from app.modules.role.service import RoleService


class UserDetailComposer:
    def __init__(self, user_service: UserService, role_service: RoleService):
        self.user_service = user_service
        self.role_service = role_service

    async def compose(self, user_id: str) -> dict:
        # 并行获取用户和角色信息
        user = await self.user_service.get_user_by_id(user_id)
        # 假设 RoleService 有 get_roles_by_user 方法（需自行实现）
        roles = await self.role_service.list_roles()
        return {
            "user": UserResponse.model_validate(user),
            "roles": [RoleResponse.model_validate(r) for r in roles],
        }