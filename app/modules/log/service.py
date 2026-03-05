# app/modules/log/service.py（最终融合版）
from enum import Enum
from typing import Optional, Dict

from app.core.log_processor import AsyncLogProcessor

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    AUDIT = "AUDIT"  # 审计级（合规必留）

class LogService:
    def __init__(self):
        self.processor = AsyncLogProcessor()

    async def log(
        self,
        operation_type: str,
        module: str,
        operator_id: Optional[str] = None,
        operator_name: Optional[str] = None,
        content: Optional[Dict] = None,
        result: str = "SUCCESS",
        error_detail: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        level: LogLevel = LogLevel.INFO,
        # 新增API关联参数
        request_id: Optional[str] = None,
        api_path: Optional[str] = None,
        http_method: Optional[str] = None,
    ):
        """统一日志入口，支持分级"""
        log_data = {
            "operation_type": operation_type,
            "module": module,
            "operator_id": operator_id,
            "operator_name": operator_name,
            "content": content,
            "result": result,
            "error_detail": error_detail,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "level": level.value,
            "request_id": request_id,
            "api_path": api_path,
            "http_method": http_method,
        }
        await self.processor.log(log_data)