"""
日志模块服务层
app/core/log/service.py
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.log.context import LogContext
# from app.modules.audit.models import SysAccessLog, SysErrorLog

# 配置日志
# logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class LogService:
    """统一日志服务（无状态设计）（使用延迟导入）"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def record_access_log(self, session: AsyncSession, log_context: LogContext) -> None:
        """异步记录系统访问日志"""
        # 运行时导入，避免循环依赖
        from app.modules.audit.models import SysAccessLog

        try:
            """接收LogContext，统一转换为数据库模型"""
            # 安全解析上下文
            log_dict = self._safe_serialize(log_context)

            # 关键修复：更健壮的 operator_id 提取逻辑
            operator_id = None
            user_context = log_dict.get("user_context")
            if user_context and isinstance(user_context, dict):
                operator_id = user_context.get("id")
            # 兼容旧格式
            elif user_context and hasattr(user_context, "id"):
                operator_id = user_context.id


            # 关键修复：None 安全检查
            request_params = log_dict.get("request_params", {})
            query_params = request_params.get("query_params", {}) if isinstance(request_params, dict) else {}
            body = request_params.get("body", "") if isinstance(request_params, dict) else ""

            log = SysAccessLog(
                request_id=log_dict.get("request_id", ""),
                request_uri=log_dict.get("request_uri", ""),
                request_method=log_dict.get("request_method", ""),
                request_params=json.dumps(query_params),
                request_body=body,
                http_status=log_dict.get("http_status", 500),
                execution_time=log_dict.get("execution_time", 0),
                ip=log_dict.get("ip", ""),
                user_agent=log_dict.get("user_agent", ""),
                operator_id=operator_id,  # 使用提取的 operator_id
                # operator_id=log_dict.get("user_context", {}).get("id") if log_dict.get("user_context") else None,
                handler=log_dict.get("handler", "")
            )
            session.add(log)
        except Exception as e:
            logger.error(f"记录访问日志失败: {e}", exc_info=True)
            raise


    async def record_error_log(
        self,
        session: AsyncSession,
        log_context: LogContext,
        error_code: str,
        error_msg: str,
        error_stack: str,
    ) -> None:
        """异步记录错误日志"""
        # 运行时导入
        from app.modules.audit.models import SysErrorLog

        try:
            """错误日志复用同一上下文"""
            log_dict = self._safe_serialize(log_context)

            # 关键修复：更健壮的 operator_id 提取逻辑
            operator_id = None
            user_context = log_dict.get("user_context")
            if user_context and isinstance(user_context, dict):
                operator_id = user_context.get("id")
            elif user_context and hasattr(user_context, "id"):
                operator_id = user_context.id


            # 关键修复：None 安全检查
            request_params = log_dict.get("request_params", {})
            query_params = request_params.get("query_params", {}) if isinstance(request_params, dict) else {}
            body = request_params.get("body", "") if isinstance(request_params, dict) else ""

            log = SysErrorLog(
                request_id=log_dict.get("request_id", ""),
                request_uri=log_dict.get("request_uri", ""),
                request_method=log_dict.get("request_method", ""),
                request_params=json.dumps(query_params),
                request_body=body,
                ip=log_dict.get("ip", ""),
                user_agent=log_dict.get("user_agent", ""),
                operator_id=operator_id,  # 使用提取的 operator_id
                # operator_id=log_dict.get("user_context", {}).get("id") if log_dict.get("user_context") else None,
                handler=log_dict.get("handler", ""),
                error_code=error_code,
                error_msg=error_msg,
                error_stack=error_stack
            )
            # 脱敏处理
            if hasattr(log, 'set_error_stack'):
                log.set_error_stack(error_stack)
            session.add(log)
        except Exception as e:
            logger.error(f"记录错误日志失败: {e}", exc_info=True)
            raise


    @staticmethod
    def _safe_serialize(obj) -> Dict[str, Any]:
        """安全序列化对象"""
        if obj is None:
            return {}
        # 处理 dataclass 对象
        if hasattr(obj, '__dict__'):
            result = obj.__dict__.copy()
            # 递归序列化嵌套对象
            for key, value in result.items():
                if hasattr(value, '__dict__'):
                    result[key] = value.__dict__.copy()
            return result
        elif isinstance(obj, dict):
            return obj.copy()
        return {}


    # @staticmethod
    # def generate_request_id() -> str:
    #     """生成request_id（工具方法，无状态）"""
    #     return str(uuid.uuid4())