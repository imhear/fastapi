"""
业务审计日志中间件
app/core/middleware/audit_middleware.py
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.core.database import create_log_session
from app.core.container import Container
from app.core.dataclasses import AuditContext, UserContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger

# 使用结构化日志器
logger = get_logger("audit_log")

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
        # 1. 获取预生成的LogContext
        log_context = getattr(request.state, "log_context", None)
        if not log_context:
            logger.error(f"审计日志缺少日志上下文 log_context")
            return # 无上下文时直接返回，避免后续报错

        # 1. 检查是否有审计上下文（无则跳过）
        request_id = log_context.request_id
        audit_context: AuditContext = getattr(request.state, "audit_context", None)
        if not audit_context:
            logger.error(f"审计日志缺少审计上下文 audit_context")
            return
        if audit_context.operation_result is None:
            logger.error(f"审计上下文缺少 operation_result，request_id: {getattr(request.state, 'request_id', '')}")

        # 2. 获取用户上下文 TODO 有些操作无需登录，是否应该分情况讨论
        user_context: UserContext = log_context.user_context
        if not user_context:
            logger.warning(f"审计日志缺少用户上下文 - request_id: {getattr(request.state, 'request_id', '')}")
            return

        user_id = user_context.id if user_context else None
        username = user_context.username if user_context else None

        # 3. 结构化日志输出（核心新增）
        logger.info(
            "audit_log",
            request_id=request_id,  # 强制传入
            module=audit_context.module,
            operation_type=audit_context.operation_type,
            business_id=audit_context.business_id,
            operation_content=audit_context.operation_content,
            operation_result=audit_context.operation_result or "UNKNOWN",
            error_msg=audit_context.error_msg,
            operator_id=user_id,
            operator_name=username
        )

        # 4. 独立会话记录日志（核心：不参与业务事务）
        log_session: AsyncSession = None
        try:
            log_session = await create_log_session()
            log_service = Container.log_service()

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
            logger.error("audit_log_db_write_error", error=str(e), exc_info=True)
        finally:
            if log_session:
                await log_session.close()