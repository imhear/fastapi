# app/core/middleware.py
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    """全局中间件：为每个请求生成唯一request_id，用于链路追踪"""
    async def dispatch(self, request: Request, call_next):
        # 生成request_id（优先使用客户端传入的X-Request-ID，无则生成）
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        # 响应头返回request_id，方便客户端关联
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response