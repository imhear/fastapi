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
    is_deleted = Column(SmallInteger, default=0)

    roles = relationship('SysRole', secondary='sys_user_role', back_populates='users')