"""
用户上下文数据类
app/core/dataclasses.py
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class UserContext:
    """用户上下文数据类（仅存储需要的字段，无ORM依赖）"""
    id: Optional[int] = None
    username: Optional[str] = None
    is_superuser: Optional[bool] = None

@dataclass
class AuditContext:
    """业务审计上下文（标准化透传字段）"""
    module: str  # 业务模块：user/role/order
    operation_type: str  # 操作类型：CREATE/UPDATE/DELETE
    business_id: str  # 被操作资源ID
    operation_content: Dict[str, Any]  # 操作详情
    operation_result: str = "SUCCESS"  # SUCCESS/FAILURE
    error_msg: Optional[str] = None  # 失败时的错误信息