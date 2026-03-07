# app/composers/user_update_composer.py
from app.core.uow import SqlAlchemyUoW
from app.domain.role.interfaces import AbstractRoleService
from app.domain.user.interfaces import AbstractUserService
# from app.modules.user.service import UserService
# from app.modules.role.service import RoleService
from app.modules.user.schemas import UserUpdate
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class UserUpdateComposer:
    def __init__(
        self,
        user_service: AbstractUserService,
        role_service: AbstractRoleService,
    ):
        self.user_service = user_service
        self.role_service = role_service

    async def update_user_with_roles(
        self,
        session: AsyncSession,
        user_id: str,
        user_update: UserUpdate,
        current_version: int,
        current_user_id: str,
    ) -> dict:
        # 开启一个原子事务
        # async with SqlAlchemyUoW(self._session_factory) as uow:
        # 1. 更新用户基本信息（只更新用户字段）
        updated_user = await self.user_service.update_user(
            session=session,
            user_id=user_id,
            user_update=user_update,
            current_version=current_version,
            current_user_id=current_user_id
        )

        # 2. 分配角色（如果提供了 role_ids）
        if user_update.role_ids is not None:
            await self.role_service.assign_roles_to_user(
                session=session,
                user_id=user_id,
                role_ids=user_update.role_ids,
            )
            # 3. 获取最新的角色列表（关键：传入uow.session，复用事务内会话）
            roles = await self.role_service.get_roles_by_user_id(
                session=session,
                user_id=user_id,
            )

        # 退出上下文时自动提交
        return {
            "user": updated_user,
            "roles": roles
        }