# app/modules/user/models.py
from sqlalchemy import Column, String, SmallInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, uuid_pk_column

sys_user_role = Table(
    'sys_user_role',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('sys_user.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('sys_role.id'), primary_key=True),
)


class SysUser(Base):
    __tablename__ = 'sys_user'

    id = uuid_pk_column()
    username = Column(String(64), unique=True, nullable=False)
    nickname = Column(String(64))
    password = Column(String(100), nullable=False)
    email = Column(String(128))
    is_deleted = Column(SmallInteger, default=0, comment='逻辑删除标识(0-未删除 1-已删除)')
    status = Column(SmallInteger, default=1, comment='状态(1-正常 0-禁用)')
    is_superuser = Column(SmallInteger, default=0, comment='超级用户(1-是 0-否)')

    roles = relationship('SysRole', secondary='sys_user_role', back_populates='users')