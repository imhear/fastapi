# app/modules/log/schemas.py（新增）
from enum import Enum
from typing import Optional

from pydantic import BaseModel

class LogLevel(str, Enum):
    DEBUG = "DEBUG"       # 调试日志
    INFO = "INFO"         # 普通操作
    WARN = "WARN"         # 警告操作
    ERROR = "ERROR"       # 错误操作
    AUDIT = "AUDIT"       # 审计级（合规必留）

class BusinessLogCreate(BaseModel):
    operation_type: str
    module: str
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    content: Optional[dict] = None
    result: str = "SUCCESS"
    error_detail: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    level: LogLevel = LogLevel.INFO
    # 新增字段
    request_id: Optional[str] = None
    api_path: Optional[str] = None
    http_method: Optional[str] = None

# 日志服务中新增level参数，存储时增加level字段，检索时可按级别过滤