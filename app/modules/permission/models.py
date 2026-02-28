from sqlalchemy import Column, String, Boolean, SmallInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

# 角色-权限关联表
# sys_role_permission = Table(
#     'sys_role_permission',
#     Base.metadata,
#     Column('role_id', ForeignKey('sys_role.id'), primary_key=True),
#     Column('permission_id', ForeignKey('sys_permission.id'), primary_key=True),
# )

class SysPermission(BaseModel):
    __tablename__ = 'sys_permission'

    # id = uuid_pk_column()
    code = Column(String(64), unique=True, nullable=False)      # 权限代码（如 user:create）
    name = Column(String(64), nullable=False)                   # 权限名称
    description = Column(String(255))                            # 描述
    category = Column(String(64), default='general')            # 分类
    # is_active = Column(Boolean, default=True)                    # 是否激活
    # status = Column(SmallInteger, default=1)
    # is_deleted = Column(SmallInteger, default=0)

    roles = relationship('SysRole', secondary='sys_role_permission', back_populates='permissions')