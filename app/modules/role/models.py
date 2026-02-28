# app/modules/role/models.py
from sqlalchemy import Column, String, SmallInteger, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel

# 角色-权限关联表
sys_role_permission = Table(
    'sys_role_permission',
    BaseModel.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('sys_role.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('sys_permission.id'), primary_key=True),
)


class SysRole(BaseModel):
    __tablename__ = 'sys_role'

    # id = uuid_pk_column()
    name = Column(String(64), unique=True, nullable=False)
    code = Column(String(32), unique=True, nullable=False)
    # status = Column(SmallInteger, default=1)
    # is_deleted = Column(SmallInteger, default=0)

    users = relationship('SysUser', secondary='sys_user_role', back_populates='roles')
    permissions = relationship('SysPermission', secondary='sys_role_permission', back_populates='roles')
