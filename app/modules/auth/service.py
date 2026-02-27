# app/modules/auth/service.py
from typing import Optional
from jose import JWTError

from app.core.security import decode_jwt_token, verify_password
from app.domain.auth.interfaces import AbstractAuthService
from app.domain.user.interfaces import AbstractUserService
from app.domain.redis.interfaces import AbstractRedisService
from app.modules.user.models import SysUser
from app.modules.auth.schemas import TokenPayload
from fastapi import HTTPException, status


class AuthService(AbstractAuthService):
    def __init__(self, user_service: AbstractUserService, redis_service: AbstractRedisService):
        self.user_service = user_service
        self.redis_service = redis_service

    async def authenticate_user(self, username: str, password: str) -> Optional[SysUser]:
        """验证用户名密码，成功返回用户对象"""
        user = await self.user_service.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        if not user.status == 1 or user.is_deleted == 1:
            return None
        return user

    async def get_current_user(self, token: str) -> SysUser:
        """从 JWT token 获取当前用户"""
        try:
            payload = decode_jwt_token(token)
            token_data = TokenPayload(**payload)
        except (JWTError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Could not validate credentials: {str(e)}"
            )

        user = await self.user_service.get_user_by_id(token_data.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not user.status == 1 or user.is_deleted == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user