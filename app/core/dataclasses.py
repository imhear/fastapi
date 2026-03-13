"""
用户上下文数据类
app/core/dataclasses.py
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserContext:
    """用户上下文数据类（仅存储需要的字段，无ORM依赖）"""
    id: Optional[int] = None
    username: Optional[str] = None
    is_superuser: Optional[bool] = None