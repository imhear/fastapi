"""
全局异常处理器中间件
app/core/exception/handler.py
"""
import logging
import traceback

from app.core.database import create_log_session
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.container import Container
from sqlalchemy.ext.asyncio import AsyncSession

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

    # 2. 记录错误日志
    request_id = getattr(request.state, "request_id", Container.log_service().generate_request_id())
    log_service = Container.log_service()

    # 显式创建日志会话
    log_session: AsyncSession = None
    try:
        log_session = await create_log_session()
        await log_service.record_error_log(
            session=log_session,          # 关键：传入 session
            request_id=request_id,
            error_code=str(status_code),
            error_msg=str(exc),
            error_stack=traceback.format_exc(),
            request_uri=str(request.url)
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