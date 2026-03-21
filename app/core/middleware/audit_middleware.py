# app/core/middleware/audit_middleware.py
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.core.database import create_log_session
from app.core.container import Container
from app.core.dataclasses import AuditContext, UserContext
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BizAuditLogMiddleware(BaseHTTPMiddleware):
    """业务审计日志中间件（独立会话，异步记录）"""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = None
        try:
            # 执行API逻辑（先处理业务，再记录日志）
            response = await call_next(request)
            return response

        except Exception as e:
            # 捕获异常不影响日志记录（交给全局异常处理器）
            raise

        finally:
            # 核心：无论成功/失败，都记录审计日志（独立try块，不影响主流程）
            await self._record_audit_log(request)

    async def _record_audit_log(self, request: Request):
        """异步记录业务审计日志（独立会话）"""
        # 1. 检查是否有审计上下文（无则跳过）
        audit_context: AuditContext = getattr(request.state, "audit_context", None)
        if not audit_context:
            return
        if audit_context.operation_result is None:
            logger.error(f"审计上下文缺少 operation_result，request_id: {getattr(request.state, 'request_id', '')}")

        # 2. 获取用户上下文
        user_context: UserContext = getattr(request.state, "user_context", None)
        if not user_context:
            logger.warning(f"审计日志缺少用户上下文 - request_id: {getattr(request.state, 'request_id', '')}")
            return

        # 3. 独立会话记录日志（核心：不参与业务事务）
        log_session: AsyncSession = None
        try:
            log_session = await create_log_session()
            log_service = Container.log_service()
            log_context = getattr(request.state, "log_context", None)

            # 调用审计服务记录日志（复用原有AuditService，仅修改会话来源）
            await log_service.record_audit_log(
                db=log_session,  # 使用日志独立会话
                log_context=log_context,
                audit_context=audit_context
            )
            await log_session.commit()

        except Exception as e:
            if log_session and log_session.is_active:
                await log_session.rollback()
            logger.error(f"记录业务审计日志失败: {e}", exc_info=True)

        finally:
            if log_session:
                await log_session.close()