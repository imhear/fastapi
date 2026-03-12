# app/core/log/context.py
from dataclasses import dataclass
from typing import Optional
from fastapi import Request

@dataclass
class LogContext:
    """日志上下文（封装通用参数）"""
    request_id: str
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None

    @classmethod
    def from_request(cls, request: Request) -> "LogContext":
        """从Request自动提取上下文"""
        user = getattr(request.state, "user", None)
        return cls(
            request_id=getattr(request.state, "request_id", ""),
            operator_id=str(user.id) if user else None,
            operator_name=user.username if user else None,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "")
        )

def generate_request_id() -> str:
    """生成全局唯一request_id"""
    import uuid
    return str(uuid.uuid4())