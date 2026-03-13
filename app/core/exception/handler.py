"""
全局异常处理器中间件
app/core/exception/handler.py
"""
import json
import logging
import traceback
from typing import Optional

from app.config.config import settings
from app.core.database import create_log_session
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.container import Container
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def _desensitize_body(body: bytes) -> Optional[str]:
    """请求体脱敏（与中间件保持一致，可考虑提取到公共模块）"""
    try:
        data = json.loads(body)
        sensitive_fields = ["password", "token", "secret", "mobile", "id_card"]
        for field in sensitive_fields:
            if field in data:
                data[field] = "***"
        return json.dumps(data)
    except Exception:
        return body.decode("utf-8", errors="ignore")[:settings.LOG_MAX_BODY_SIZE]


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    # 1. 基础响应
    status_code = getattr(exc, "status_code", 500)
    response = JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "msg": "服务器内部错误" if status_code == 500 else str(exc)
        }
    )

    # 2. 提取请求上下文
    request_id = getattr(request.state, "request_id", Container.log_service().generate_request_id())
    # 获取请求体（利用中间件已读取的 _body）
    request_body = None
    if settings.LOG_RECORD_BODY and request.method in ["POST", "PUT", "PATCH"]:
        try:
            # 从 request._body 获取（由 AccessLogMiddleware 预先读取）
            body = getattr(request, "_body", None)
            if body is None:
                body = await request.body()
            if len(body) < settings.LOG_MAX_BODY_SIZE:
                request_body = _desensitize_body(body)
        except Exception:
            request_body = "无法解析的请求体"

    # 获取用户信息（如果已认证）（使用上下文而非ORM实例）
    user_context = getattr(request.state, "user_context", None)
    # operator_id = user_context.id if (user_context and hasattr(user_context, "id")) else None
    # 异常处理器中operator_id的最终优化版
    try:
        user_context = getattr(request.state, "user_context", None)
        operator_id = user_context.id if (user_context and hasattr(user_context, "id")) else None
    except Exception:
        operator_id = None
    # user = getattr(request.state, "user", None)  # 获取user,由系统访问日志中间件存入，但不确定系统访问日志中间件是否真的存入
    # operator_id = user.id if (user and hasattr(user, "id")) else None
    handler = getattr(request.state, "handler", None)  # 获取处理器函数名,由系统访问日志中间件存入

    # 2. 记录错误日志（包含完整上下文）
    log_service = Container.log_service()
    # 显式创建日志会话
    log_session: AsyncSession = None
    try:
        log_session = await create_log_session()
        await log_service.record_error_log(
            session=log_session,
            request_id=request_id,
            error_code=str(status_code),
            error_msg=str(exc),
            error_stack=traceback.format_exc(),
            request_uri=str(request.url),
            # 新增参数
            request_method=request.method,
            request_params=json.dumps(dict(request.query_params)),
            request_body=request_body,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            operator_id=operator_id,
            handler=handler,
        )
        await log_session.commit()
    except Exception as e:
        if log_session and not log_session.is_active:
            await log_session.rollback()
        logger.error(f"记录错误日志失败: {e}", exc_info=True)
    finally:
        if log_session and not log_session.is_active:
            await log_session.close()

    return response
