from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import inject, Provide
from jose import JWTError

from app.core.security import extract_token_subject
from app.domain.user.interfaces import AbstractUserService
from app.di.container import Container

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: AbstractUserService = Depends(Provide[Container.user_container.user_service])
):
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
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # 可选：检查用户是否激活
    # if not user.is_active:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    return user