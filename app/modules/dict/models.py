"""
数据字典模型
app/modules/dict/models.py
"""
from sqlalchemy import Column, String, ForeignKey, Integer, BigInteger, Text
from sqlalchemy.orm import relationship
from app.core.database import BaseTableModel


class Dict(BaseTableModel):
    __tablename__ = 'sys_dict'
    __table_args__ = {'comment': '数据字典类型表'}

    dict_code = Column(String(36), unique=True, nullable=False, comment='类型编码')
    name = Column(String(50), unique=True, nullable=False, comment='类型名称')
    remark = Column(Text, nullable=True, comment='备注')
    # 关联关系
    # items = relationship('DictItem', back_populates='dict', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Dict(id={self.id}, code={self.dict_code}, name={self.name})>"


class DictItem(BaseTableModel):
    __tablename__ = 'sys_dict_item'
    __table_args__ = {'comment': '数据字典项表'}

    # dict_id = Column(BigInteger, ForeignKey('sys_dict.id'), nullable=False, comment='数据字典类型ID')
    dict_code = Column(String(36), nullable=False, comment='关联字典编码，与sys_dict表中的dict_code对应')

    # 字典项内容
    value = Column(String(50), nullable=False, comment='字典项值')
    label = Column(String(100), nullable=True, comment='字典项标签')
    tag_type = Column(String(50), nullable=True, comment='标签类型，用于前端样式展示（如success、warning等）')
    sort = Column(Integer, default=0, comment='排序')
    remark = Column(Text, nullable=True, comment='备注')
    # 关联关系
    # dict = relationship('Dict', back_populates='items')

    def __repr__(self):
        return f"<DictItem(id={self.id}, value={self.value}, label={self.label})>"