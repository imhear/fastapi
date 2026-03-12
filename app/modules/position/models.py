"""
系统岗位模型
app/modules/position/models.py
"""
from sqlalchemy import Column, String
from app.core.database import BaseTableModel


class Position(BaseTableModel):
    __tablename__ = 'sys_position'
    __table_args__ = {'comment': '系统岗位表'}

    code = Column(String(32), unique=True, nullable=False, comment='岗位编码')
    name = Column(String(64), unique=True, nullable=False, comment='岗位名称')
