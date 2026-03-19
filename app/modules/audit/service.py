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
        operator_id: int,
        operator_name: str,
        log_context: LogContext,  # 复用上下文
        module: str,
        operation_type: str,
        business_id: str,
        operation_content: str,
        operation_result: str = "SUCCESS",
        error_msg: Optional[str] = None,
    ) -> None:
        """记录业务审计日志（独立会话，手动提交）"""
        try:
            log = BizAuditLog(
                operator_id=operator_id,
                operator_name=operator_name,
                module=module,
                operation_type=operation_type,
                business_id=business_id,
                operation_content=operation_content,
                operation_result=operation_result,
                error_msg=error_msg,
                # 新增：空值保护
                ip_address=log_context.ip if log_context else "",
                request_id=log_context.request_id if log_context else ""
            )
            db.add(log)
            # 移除：不再依赖业务事务提交，由中间件手动commit
        except Exception as e:
            # 仅记录错误，不抛异常
            logger.error(f"业务审计日志记录失败: {e}", exc_info=True)
            raise  # 抛出异常，让中间件处理回滚