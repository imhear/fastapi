"""
API 依赖项配置文件
backend/app/api/deps.py
"""
from app.core.auth import get_current_user
from app.modules.user.models import SysUser
from fastapi import Depends
from typing import Annotated

