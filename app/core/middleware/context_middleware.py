"""
请求上下文中间件
app/core/middleware/context_middleware.py
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.log.context import LogContext
from app.core.log.context import generate_request_id


class ContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件（所有请求的第一个中间件）"""

    async def dispatch(self, request: Request, call_next):
        # 1. 生成全局唯一request_id
        request_id = generate_request_id()
        request.state.request_id = request_id

        # 2. 获取用户上下文（提前初始化，即使还未认证）
        user_context = getattr(request.state, "user_context", None)

        # 3. 安全获取客户端信息
        try:
            client_host = request.client.host if request.client else ""
        except Exception:
            client_host = ""

        try:
            user_agent = request.headers.get("user-agent", "")
        except Exception:
            user_agent = ""

        # 4. 预生成LogContext（包含用户上下文）
        request.state.log_context = LogContext(
            request_id=request_id,
            request_uri=str(request.url.path),
            request_method=request.method,
            ip=client_host,
            user_agent=user_agent,
            user_context=user_context  # 关键：传递用户上下文
        )

        # 5. 执行后续中间件/路由（安全处理）
        try:
            response = await call_next(request)

            # 6. 请求处理完成后，更新用户上下文（认证后的值）
            updated_user_context = getattr(request.state, "user_context", None)
            if updated_user_context:
                request.state.log_context.user_context = updated_user_context

            # 7. 补充响应信息到上下文
            if response is not None:
                request.state.log_context.http_status = response.status_code
            return response
        except Exception:
            # 即使后续中间件出错，也要返回响应
            raise
