"""
系统用户模型
app/modules/user/models.py
"""
from sqlalchemy import Column, String, SmallInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import BaseTableModel


class User(BaseTableModel):
    __tablename__ = 'sys_user'
    __table_args__ = {'comment': '系统用户表'}

    username = Column(String(64), unique=True, nullable=False, comment='登录账号')
    nickname = Column(String(64), comment='用户昵称')
    password = Column(String(100), nullable=False, comment='加密密码')
    email = Column(String(128), comment='邮箱')
    is_superuser = Column(SmallInteger, default=0, comment='超级用户(1-是 0-否)')

    # 关系
    dept_positions = relationship('DeptPosition', secondary='sys_dept_position_user', back_populates='users')
