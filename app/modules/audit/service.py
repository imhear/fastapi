"""
业务审计日志模块服务层
app/modules/audit/service.py
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.log.context import LogContext
from app.modules.audit.models import BizAuditLog

logger = logging.getLogger(__name__)

class AuditService:
    """业务审计服务（与业务同事务）"""

    async def record_audit_log(
        self,
        db: AsyncSession,
        log_context: LogContext,  # 复用上下文
        # operator_id: int,
        # operator_name: str,
        module: str,
        operation_type: str,
        business_id: str,
        operation_content: str,
        operation_result: str = "SUCCESS",
        error_msg: Optional[str] = None,
        # ip_address: Optional[str] = None,
        # request_id: Optional[str] = None
    ) -> None:
        """记录业务审计日志（异常隔离，不影响主事务）"""
        try:
            log = BizAuditLog(
                operator_id=log_context.user_context.id if log_context.user_context else None,
                operator_name=log_context.user_context.username if log_context.user_context else None,
                module=module,
                operation_type=operation_type,
                business_id=business_id,
                operation_content=operation_content,
                operation_result=operation_result,
                error_msg=error_msg,
                ip_address=log_context.ip,
                request_id=log_context.request_id
            )
            db.add(log)
        except Exception as e:
            # 仅记录错误，不抛异常
            logger.error(f"业务审计日志记录失败: {e}", exc_info=True)