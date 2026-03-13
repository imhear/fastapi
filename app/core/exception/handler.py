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
# 关键：导入 RequestParams 类
from app.core.log.context import LogContext, RequestParams, generate_request_id

logger = logging.getLogger(__name__)

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
    # 2. 直接复用已封装的LogContext
    log_context = getattr(request.state, "log_context", None)
    if not log_context:
        # 降级处理：如果上下文未初始化，手动创建
        # from app.core.log.context import LogContext, generate_request_id
        log_context = LogContext(
            request_id=generate_request_id(),
            request_uri=str(request.url.path),
            request_method=request.method,
            ip=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", "")
        )

    # 3. 强制更新用户上下文（关键修复）
    user_context = getattr(request.state, "user_context", None)
    if user_context:
        log_context.user_context = user_context

    # 4. 补充异常相关的请求体信息
    if settings.LOG_RECORD_BODY and request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = getattr(request, "_body", None)
            if body is None:
                body = await request.body()

            # 关键修复：直接调用静态方法，而非通过实例
            body_str = LogContext._desensitize_body(body)

            if log_context.request_params:
                log_context.request_params.body = body_str
            else:
                log_context.request_params = RequestParams(
                    path_params=dict(request.path_params),
                    query_params=dict(request.query_params),
                    body=body_str
                )
        except Exception as e:
            logger.warning(f"处理请求体失败: {e}")

    # 5. 记录错误日志（包含完整上下文）
    log_session: AsyncSession = None
    try:
        log_session = await create_log_session()  # 显式创建日志会话
        log_service = Container.log_service()
        # 2. 仅补充错误专属字段
        await log_service.record_error_log(
            session=log_session,
            log_context=log_context,  # 统一上下文
            error_code=str(status_code),
            error_msg=str(exc),
            error_stack=traceback.format_exc()
        )
        await log_session.commit()
    except Exception as e:
        if log_session and log_session.is_active:
            await log_session.rollback()
        logger.error(f"记录错误日志失败: {e}", exc_info=True)
    finally:
        if log_session:
            try:
                await log_session.close()
            except Exception:
                pass

    return response
