"""
系统角色模型
app/modules/role/models.py
"""
from sqlalchemy import Column, String, BigInteger, Text, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.core.database import BaseTableModel, Base

# 角色-权限关联表
class RolePermission(Base):
    __tablename__ = 'sys_role_permission'
    __table_args__ = (
        PrimaryKeyConstraint('role_id', 'permission_id'),
        {'comment': '角色-权限关联表'}
    )
    role_id = Column(BigInteger, ForeignKey('sys_role.id'), nullable=False)
    permission_id = Column(BigInteger, ForeignKey('sys_permission.id'), nullable=False)

# 角色-菜单关联表
class RoleMenu(Base):
    __tablename__ = 'sys_role_menu'
    __table_args__ = (
        PrimaryKeyConstraint('role_id', 'menu_id'),
        {'comment': '角色-菜单关联表'}
    )
    role_id = Column(BigInteger, ForeignKey('sys_role.id'), nullable=False)
    menu_id = Column(BigInteger, ForeignKey('sys_menu.id'), nullable=False)

# 角色主表
class Role(BaseTableModel):
    __tablename__ = 'sys_role'
    __table_args__ = {'comment': '系统角色表'}

    code = Column(String(32), unique=True, nullable=False, comment='角色编码')
    name = Column(String(64), unique=True, nullable=False, comment='角色名称')
    remark = Column(Text, nullable=True, comment='角色备注')

    # 关联关系
    menus = relationship('Menu', secondary='sys_role_menu', back_populates='roles')
    permissions = relationship('Permission', secondary='sys_role_permission', back_populates='roles')
    dept_positions = relationship('DeptPosition', secondary='sys_dept_position_role', back_populates='roles')
