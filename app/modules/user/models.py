# app/modules/user/models.py
from sqlalchemy import Column, String, SmallInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import BaseTableModel

class SysUser(BaseTableModel):
    __tablename__ = 'sys_user'

    username = Column(String(64), unique=True, nullable=False)
    nickname = Column(String(64))
    password = Column(String(100), nullable=False)
    email = Column(String(128))


    is_superuser = Column(SmallInteger, default=0, comment='超级用户(1-是 0-否)')

    roles = relationship('SysRole', secondary='sys_user_role', back_populates='users')