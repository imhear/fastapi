"""
日志模块服务层
app/core/log/service.py
"""
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.models import SysAccessLog, SysErrorLog

# 配置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class LogService:
    """统一日志服务（无状态设计）- 不持有session，外部显式传入"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def record_access_log(self, session: AsyncSession, log_data: Dict[str, Any]) -> None:
        """异步记录系统访问日志"""
        try:
            log = SysAccessLog(**log_data)
            session.add(log)
        except Exception as e:
            logger.error(f"系统访问日志写入失败: {e}", exc_info=True)
            raise


    async def record_error_log(
        self,
        session: AsyncSession,
        request_id: str,
        error_code: str,
        error_msg: str,
        error_stack: str,
        request_uri: Optional[str] = None,
        # 新增参数
        request_method: Optional[str] = None,
        request_params: Optional[str] = None,
        request_body: Optional[str] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        operator_id: Optional[int] = None,
        handler: Optional[str] = None,
    ) -> None:
        """异步记录错误日志"""
        try:
            log = SysErrorLog(
                request_id=request_id,
                error_code=error_code,
                error_msg=error_msg,
                request_uri=request_uri,
                # 新增参数
                request_method=request_method,
                request_params=request_params,
                request_body=request_body,
                ip=ip,
                user_agent=user_agent,
                operator_id=operator_id,
                handler=handler,
            )
            log.set_error_stack(error_stack)
            session.add(log)
        except Exception as e:
            logger.error(f"错误日志写入失败: {e}", exc_info=True)
            raise


    @staticmethod
    def generate_request_id() -> str:
        """生成request_id（工具方法，无状态）"""
        return str(uuid.uuid4())