# app/modules/role/models.py
from sqlalchemy import Column, String, SmallInteger, Table, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import BaseTableModel, Base

# 角色-权限关联表
# sys_role_permission = Table(
#     'sys_role_permission',
#     Base.metadata,
#     Column('role_id', UUID(as_uuid=True), ForeignKey('sys_role.id'), primary_key=True),
#     Column('permission_id', UUID(as_uuid=True), ForeignKey('sys_permission.id'), primary_key=True),
# )
#
# # 角色-用户关联表模型（不继承 BaseModel）
class SysRolePermission(Base):
    __tablename__ = 'sys_role_permission'

    permission_id = Column(UUID(as_uuid=True), ForeignKey('sys_permission.id'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('sys_role.id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('permission_id', 'role_id'),
    )

class SysRole(BaseTableModel):
    __tablename__ = 'sys_role'

    # id = uuid_pk_column()
    name = Column(String(64), unique=True, nullable=False)
    code = Column(String(32), unique=True, nullable=False)
    # status = Column(SmallInteger, default=1)
    # is_deleted = Column(SmallInteger, default=0)

    users = relationship('SysUser', secondary='sys_user_role', back_populates='roles')
    permissions = relationship('SysPermission', secondary='sys_role_permission', back_populates='roles')

# 角色-用户关联表模型（不继承 BaseModel）
class SysUserRole(Base):
    __tablename__ = 'sys_user_role'

    user_id = Column(UUID(as_uuid=True), ForeignKey('sys_user.id'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('sys_role.id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'role_id'),
    )
