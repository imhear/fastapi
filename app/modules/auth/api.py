# app/modules/auth/api.py

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import inject, Provide
from jose import JWTError

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, refresh_access_token
from app.core.email import generate_password_reset_token, generate_reset_password_email, send_email, verify_password_reset_token
from app.domain.user.interfaces import AbstractUserService
from app.domain.redis.interfaces import AbstractRedisService
from app.services.captcha_service import CaptchaService
from app.modules.auth.schemas import LoginRequest, TokenResponse, RefreshRequest, Message, NewPassword
from app.modules.auth.service import AuthService
from app.di.container import Container
from app.core.auth import get_current_user
from app.modules.user.models import SysUser

router = APIRouter(tags=["login"])


@router.get("/captcha")
@inject
async def generate_captcha(
    captcha_service: CaptchaService = Depends(Provide[Container.captcha_service]),
) -> dict:
    """生成验证码"""
    return await captcha_service.generate_captcha()


@router.post("/login", response_model=TokenResponse)
@inject
async def login(
    login_req: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_container.auth_service]),
    user_service: AbstractUserService = Depends(Provide[Container.user_container.user_service]),
    captcha_service: CaptchaService = Depends(Provide[Container.captcha_service]),
):
    """用户登录（支持验证码）"""
    # 验证验证码（如果提供）
    if login_req.captchaId and login_req.captchaCode:
        if not await captcha_service.verify_captcha(login_req.captchaId, login_req.captchaCode):
            raise HTTPException(status_code=400, detail="验证码错误")

    # 检查登录安全
    security = await captcha_service.check_login_security(login_req.username)
    if security["is_locked"]:
        raise HTTPException(status_code=400, detail="账号已被锁定，请30分钟后再试")

    # 认证用户
    user = await auth_service.authenticate_user(login_req.username, login_req.password)
    if not user:
        # 记录失败
        await captcha_service.redis_service.record_login_failure(login_req.username)
        failures = security["failures"] + 1
        if failures >= 5:
            await captcha_service.redis_service.lock_account(login_req.username, 1800)
            raise HTTPException(status_code=400, detail="密码错误次数过多，账号已被锁定30分钟")
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    if not user.status == 1:
        raise HTTPException(status_code=400, detail="用户已被禁用")

    # 登录成功，清除失败记录
    await captcha_service.redis_service.reset_login_failure(login_req.username)

    # 更新最后登录时间（如果有此方法）
    # await user_service.update_last_login(user.id)

    # 生成令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 存储刷新令牌
    await captcha_service.redis_service.cache_refresh_token(str(user.id), refresh_token, 7 * 24 * 3600)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "bearer",
        "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/login/access-token")
@inject
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(Provide[Container.auth_container.auth_service]),
    user_service: AbstractUserService = Depends(Provide[Container.user_container.user_service]),
) -> dict:
    """OAuth2 兼容的令牌获取接口"""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not user.status == 1:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 可选：更新最后登录时间
    # await user_service.update_last_login(user.id)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh-token")
@inject
async def refresh_token(
    req: RefreshRequest,
    captcha_service: CaptchaService = Depends(Provide[Container.captcha_service]),
):
    """刷新访问令牌"""
    refresh_token = req.refreshToken
    try:
        user_id = refresh_access_token(refresh_token)  # 返回用户ID
        # 检查Redis中是否存在该刷新令牌
        cached = await captcha_service.redis_service.get_refresh_token(user_id)
        if cached != refresh_token:
            raise HTTPException(status_code=401, detail="刷新令牌无效或已过期")

        # 生成新的访问令牌
        new_access_token = create_access_token(user_id)
        # 可选：重新生成刷新令牌（实现滑动过期）
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        await captcha_service.redis_service.cache_refresh_token(user_id, new_refresh_token, 7 * 24 * 3600)

        return {
            "accessToken": new_access_token,
            "refreshToken": new_refresh_token,
            "tokenType": "bearer",
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"刷新令牌无效: {str(e)}")


@router.post("/logout")
@inject
async def logout(
    current_user: SysUser = Depends(get_current_user),
    captcha_service: CaptchaService = Depends(Provide[Container.captcha_service]),
):
    """用户登出，删除刷新令牌"""
    await captcha_service.redis_service.delete_refresh_token(str(current_user.id))
    return {"message": "登出成功"}


@router.post("/login/test-token", response_model=dict)
async def test_token(current_user: SysUser = Depends(get_current_user)):
    """测试令牌有效性"""
    return {"id": str(current_user.id), "username": current_user.username}


@router.post("/password-recovery/{email}")
@inject
async def recover_password(
    email: str,
    user_service: AbstractUserService = Depends(Provide[Container.user_container.user_service]),
):
    """发送密码重置邮件"""
    user = await user_service.get_user_by_email(email)  # 假设有该方法
    if not user:
        raise HTTPException(status_code=404, detail="该邮箱不存在")

    token = generate_password_reset_token(email)
    email_data = generate_reset_password_email(email_to=user.email, email=email, token=token)
    send_email(email_to=user.email, subject=email_data.subject, html_content=email_data.html_content)
    return {"message": "密码重置邮件已发送"}


@router.post("/reset-password")
@inject
async def reset_password(
    body: NewPassword,
    auth_service: AuthService = Depends(Provide[Container.auth_container.auth_service]),
    user_service: AbstractUserService = Depends(Provide[Container.user_container.user_service]),
):
    """使用令牌重置密码"""
    email = verify_password_reset_token(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="无效或过期的令牌")

    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await user_service.update_password(user.id, body.new_password)  # 假设有该方法
    return {"message": "密码重置成功"}