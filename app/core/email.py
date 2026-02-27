import logging
from pathlib import Path
from typing import Any, Dict, Optional

import emails
from emails.template import JinjaTemplate

from app.core.config import settings


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = None,
) -> None:
    """发送邮件"""
    if not settings.emails_enabled:
        return
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"发送邮件结果: {response}")


def generate_password_reset_token(email: str) -> str:
    """生成密码重置令牌（JWT）"""
    from datetime import timedelta
    from app.core.security import create_access_token
    expires_delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    return create_access_token(email, expires_delta=expires_delta)


def verify_password_reset_token(token: str) -> Optional[str]:
    """验证密码重置令牌，返回邮箱"""
    from jose import JWTError
    from app.core.security import decode_jwt_token
    try:
        payload = decode_jwt_token(token)
        return payload.get("sub")
    except JWTError:
        return None


def generate_reset_password_email(email_to: str, email: str, token: str) -> Dict[str, Any]:
    """生成重置密码邮件内容"""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - 密码重置"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html = f"""
    <p>您好 {email_to},</p>
    <p>您正在重置 {project_name} 的密码，请点击以下链接完成重置：</p>
    <p><a href="{link}">{link}</a></p>
    <p>如果这不是您本人的操作，请忽略此邮件。</p>
    """
    return {"subject": subject, "html_content": html}