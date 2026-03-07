# app/utils/permission_checker.py"
import logging
from typing import Callable, Awaitable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from fastapi import Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.core.auth import get_current_user
from app.modules.user.models import SysUser
from app.domain.permission.interfaces import AbstractPermissionService
from app.di.container import Container

logger = logging.getLogger(__name__)


def permission_checker(session: AsyncSession, required_perm: str, strict_superuser: bool = False) -> Callable[[SysUser], Awaitable[bool]]:
    """
    权限校验依赖项工厂
    """
    @inject
    async def checker(
        current_user: SysUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db),
        permission_service: AbstractPermissionService = Depends(Provide[Container.permission_service])
    ) -> bool:
        # 超级用户豁免（可选）
        if not strict_superuser and current_user.is_superuser:
            return True

        has_perm = await permission_service.check_user_permission(session, str(current_user.id), required_perm)
        if not has_perm:
            logger.warning(f"Permission denied for user {current_user.username}: required {required_perm}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Permission denied",
                    "required_permission": required_perm
                }
            )
        return True

    return checker