"""
部门管理模型
app/modules/dept/models.py
"""
from sqlalchemy import Column, String, SmallInteger, BigInteger, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import BaseTableModel


class Dept(BaseTableModel):
    __tablename__ = 'sys_dept'
    __table_args__ = {'comment': '部门管理表'}

    name = Column(String(64), nullable=False, comment='部门名称')
    parent_id = Column(BigInteger, ForeignKey('sys_dept.id'), nullable=True, comment='上级部门ID')

    tree_path = Column(String(255), nullable=False, comment='父节点id路径')
    sort = Column(SmallInteger, default=0, comment='显示顺序')

    # 自关联关系：上级部门id
    # parent = relationship('Dept', remote_side=[id], backref='children')

    def __repr__(self):
        return f"<Dept(id={self.id}, name={self.name}, parent_id={self.parent_id})>"