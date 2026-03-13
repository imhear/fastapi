"""
系统认证服务
app/core/auth.py
"""
from typing import Annotated, Optional
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.modules.user.models import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import inject, Provide
from jose import JWTError

from app.core.security import extract_token_subject
from app.domain.user.interfaces import AbstractUserService
from app.core.container import Container
from fastapi import Request  # 添加导入
# 关键修复：从独立文件导入 UserContext
from app.core.dataclasses import UserContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


@inject
async def get_current_user(
    request: Request,  # 新增 request 参数
    token: str = Depends(oauth2_scheme),
    user_service: AbstractUserService = Depends(Provide[Container.user_service]),
    db: AsyncSession = Depends(get_async_db),
)->User:
    """
    从 JWT token 解析用户 ID，通过 UserService 获取当前用户实体。
    """
    try:
        user_id = extract_token_subject(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        user_id = int(user_id)  # 类型转换
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # 可选：检查用户是否激活
    # if not user.is_active:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    # 关键修改：存储用户基础信息而非ORM实例
    request.state.user_context = UserContext(
        id=user.id,
        username=user.username,
        is_superuser=user.is_superuser
    )
    # 保留原ORM实例供路由使用（路由内会话仍有效）
    # 将用户存入 request.state，供后续中间件使用
    request.state.user = user

    return user

# 依赖：仅超级管理员
# {"async def get_superuser(current_user: CurrentUser = Depends(get_current_user)):
#     if not current_user.is_superuser:
#         raise PermissionDenied("仅超级管理员可操作")
#     return current_use/r"}

CurrentUser = Annotated[User, Depends(get_current_user)]