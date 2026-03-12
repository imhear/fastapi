"""
系统权限模型
app/modules/permission/models.py
"""
from sqlalchemy import Column, String, Boolean, SmallInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import BaseTableModel


class Permission(BaseTableModel):
    __tablename__ = 'sys_permission'
    __table_args__ = {'comment': '系统权限表'}

    code = Column(String(64), unique=True, nullable=False, comment='权限编码（如 user:create）')
    name = Column(String(64), unique=True, nullable=False, comment='权限名称（如 创建用户）')
    # 补充：权限类型（菜单/按钮/接口）
    type = Column(String(1), default='B', comment='权限类型（M-菜单 B-按钮 I-接口）')

    roles = relationship('Role', secondary='sys_role_permission', back_populates='permissions')