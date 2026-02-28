# app/modules/user/models.py
from sqlalchemy import Column, String, SmallInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel

sys_user_role = Table(
    'sys_user_role',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('sys_user.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('sys_role.id'), primary_key=True),
)


class SysUser(BaseModel):
    __tablename__ = 'sys_user'

    username = Column(String(64), unique=True, nullable=False)
    nickname = Column(String(64))
    password = Column(String(100), nullable=False)
    email = Column(String(128))


    is_superuser = Column(SmallInteger, default=0, comment='超级用户(1-是 0-否)')

    roles = relationship('SysRole', secondary='sys_user_role', back_populates='users')