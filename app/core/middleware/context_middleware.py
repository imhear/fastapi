"""
请求上下文中间件
app/core/middleware/context_middleware.py
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.log.context import LogContext
from app.core.log.context import generate_request_id
from app.core.logging import request_id_ctx, user_context_ctx, get_logger

logger = get_logger("context_middleware")

class ContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件（所有请求的第一个中间件）"""

    async def dispatch(self, request: Request, call_next):
        # 1. 生成全局唯一request_id
        request_id = generate_request_id()
        request.state.request_id = request_id

        # 2. 绑定到structlog上下文（核心修改）
        request_id_ctx.set(request_id)

        # 3. 获取用户上下文（提前初始化，即使还未认证）
        user_context = getattr(request.state, "user_context", None)
        if user_context:
            # 将用户上下文转为字典绑定到structlog
            user_context_dict = {
                "id": user_context.id,
                "username": user_context.username,
                "is_superuser": user_context.is_superuser
            }
            user_context_ctx.set(user_context_dict)
            request.state.user_context_dict = user_context_dict


        # 4. 安全获取客户端信息
        try:
            client_host = request.client.host if request.client else ""
        except Exception:
            client_host = ""

        try:
            user_agent = request.headers.get("user-agent", "")
        except Exception:
            user_agent = ""
        content_type = request.headers.get("content-type", "")  # 获取 content_type

        # 5. 预生成LogContext（包含用户上下文）
        request.state.log_context = LogContext(
            request_id=request_id,
            request_uri=str(request.url.path),
            request_method=request.method,
            ip=client_host,
            user_agent=user_agent,
            user_context=user_context,
            content_type=content_type  # 统一设置
        )

        # 6. 记录请求上下文初始化日志
        logger.debug(
            "request_context_initialized",
            ip=client_host,
            user_agent=user_agent,
            path=request.url.path
        )

        # 7. 执行后续中间件/路由（安全处理）
        try:
            response = await call_next(request)

            # 8. 请求处理完成后，更新用户上下文（认证后的值）
            updated_user_context = getattr(request.state, "user_context", None)
            if updated_user_context:
                request.state.log_context.user_context = updated_user_context
                # 更新structlog上下文
                user_context_dict = {
                    "id": updated_user_context.id,
                    "username": updated_user_context.username,
                    "is_superuser": updated_user_context.is_superuser
                }
                user_context_ctx.set(user_context_dict)

            # 9. 补充响应信息到上下文
            if response is not None:
                request.state.log_context.http_status = response.status_code
            return response
        except Exception:
            logger.error(
                "request_context_error",
                error=str(e),
                exc_info=True
            )
            # 即使后续中间件出错，也要返回响应
            raise
