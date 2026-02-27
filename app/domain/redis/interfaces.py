# app/domain/redis/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional, Any


class AbstractRedisService(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abstractmethod
    async def delete(self, *keys: str) -> int:
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    async def expire(self, key: str, expire_seconds: int) -> bool:
        pass

    @abstractmethod
    async def incr(self, key: str) -> int:
        pass

    # 登录专用方法
    @abstractmethod
    async def cache_captcha(self, captcha_id: str, captcha_code: str, expire_seconds: int = 300) -> bool:
        pass

    @abstractmethod
    async def get_captcha(self, captcha_id: str) -> Optional[str]:
        pass

    @abstractmethod
    async def record_login_failure(self, username: str) -> int:
        pass

    @abstractmethod
    async def reset_login_failure(self, username: str) -> bool:
        pass

    @abstractmethod
    async def lock_account(self, username: str, expire_seconds: int = 1800) -> bool:
        pass

    @abstractmethod
    async def is_account_locked(self, username: str) -> bool:
        pass

    @abstractmethod
    async def cache_refresh_token(self, user_id: str, refresh_token: str, expire_seconds: int = 7 * 24 * 3600) -> bool:
        pass

    @abstractmethod
    async def get_refresh_token(self, user_id: str) -> Optional[str]:
        pass

    @abstractmethod
    async def delete_refresh_token(self, user_id: str) -> bool:
        pass