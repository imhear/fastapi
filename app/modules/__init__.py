# app/modules/__init__.py
"""
统一模型导出入口
按依赖顺序导入所有模型，确保 Base.metadata 完整
"""

import sys
from pathlib import Path

# 将项目根目录加入路径（如果尚未加入）
root = Path(__file__).parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# 1. 导入 Base（假设在 core.database 中）
from app.core.database import Base

# 2. 按依赖顺序导入各模块的模型
# 先导入无外键依赖的基础表
from app.modules.audit.models import SysAccessLog, SysErrorLog, BizAuditLog
from app.modules.dept.models import Dept
from app.modules.dict.models import Dict, DictItem
from app.modules.menu.models import Menu
from app.modules.permission.models import Permission
from app.modules.role.models import Role, RolePermission, RoleMenu
from app.modules.position.models import Position

# 再导入依赖其他表的模型
from app.modules.user.models import User
from app.modules.dept_position.models import DeptPosition, DeptPositionRole, DeptPositionUser

# 3. 导出所有模型（便于外部 from app.models import *）
__all__ = [
    'Base',
    'SysAccessLog',
    'SysErrorLog',
    'BizAuditLog',
    'Dept',
    'Dict',
    'DictItem',
    'Menu',
    'Permission',
    'Role',
    'RolePermission',
    'RoleMenu',
    'Position',
    'User',
    'DeptPosition',
    'DeptPositionRole',
    'DeptPositionUser',
]