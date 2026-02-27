"""
验证码服务层
app/services/captcha_service.py
"""
import random
import string
import base64
from typing import Dict

from app.domain.redis.interfaces import AbstractRedisService


class CaptchaService:
    def __init__(self, redis_service: AbstractRedisService):
        self.redis_service = redis_service

    async def generate_captcha(self) -> Dict[str, str]:
        """生成验证码，返回 captchaId 和 base64 图片"""
        captcha_code = ''.join(random.choices(string.digits, k=4))
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        await self.redis_service.cache_captcha(captcha_id, captcha_code, 300)

        # 生成SVG验证码图片（简单示例）
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40">
            <rect width="120" height="40" fill="#f5f5f5"/>
            <rect x="5" y="5" width="110" height="30" rx="4" fill="white" stroke="#e0e0e0" stroke-width="1"/>
            <text x="60" y="25" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold" fill="#333">
                {captcha_code}
            </text>
            <line x1="10" y1="15" x2="110" y2="30" stroke="#ccc" stroke-width="1" opacity="0.6"/>
            <line x1="20" y1="35" x2="100" y2="10" stroke="#ccc" stroke-width="1" opacity="0.6"/>
            <line x1="40" y1="8" x2="80" y2="32" stroke="#ccc" stroke-width="1" opacity="0.6"/>
        </svg>'''

        captcha_base64 = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
        return {"captchaId": captcha_id, "captchaBase64": captcha_base64}

    async def verify_captcha(self, captcha_id: str, captcha_code: str) -> bool:
        """验证验证码，验证后删除"""
        if not captcha_id or not captcha_code:
            return False
        stored = await self.redis_service.get_captcha(captcha_id)
        if not stored:
            return False
        if stored.upper() != captcha_code.upper():
            return False
        await self.redis_service.delete(f"captcha:{captcha_id}")
        return True

    async def check_login_security(self, username: str) -> dict:
        """检查登录安全状态"""
        failures = await self.redis_service.record_login_failure(username)
        is_locked = await self.redis_service.is_account_locked(username)
        return {"failures": failures, "is_locked": is_locked, "max_attempts": 5}