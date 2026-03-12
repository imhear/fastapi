"""
部门岗位管理模型
app/modules/dept_position/models.py
"""
from sqlalchemy import Column, String, SmallInteger, BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base, BaseTableModel


class DeptPositionRole(Base):
    __tablename__ = 'sys_dept_position_role'
    __table_args__ = (
        PrimaryKeyConstraint('dept_position_id', 'role_id'),
        {'comment': '部门岗位实例-角色关联表'}
    )
    dept_position_id = Column(BigInteger, ForeignKey('sys_dept_position.id'), nullable=False)
    role_id = Column(BigInteger, ForeignKey('sys_role.id'), nullable=False)


class DeptPositionUser(Base):
    __tablename__ = 'sys_dept_position_user'
    __table_args__ = (
        PrimaryKeyConstraint('dept_position_id', 'user_id'),
        {'comment': '部门岗位实例-用户关联表'}
    )
    dept_position_id = Column(BigInteger, ForeignKey('sys_dept_position.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('sys_user.id'), nullable=False)


class DeptPosition(BaseTableModel):
    __tablename__ = 'sys_dept_position'
    __table_args__ = {'comment': '部门-岗位管理表'}

    name = Column(String(64), nullable=False, comment='部门岗位实例名称')
    code = Column(String(64), nullable=False, unique=True, comment='部门岗位实例编号')
    dept_id = Column(BigInteger, ForeignKey('sys_dept.id'), nullable=False)
    position_id = Column(BigInteger, ForeignKey('sys_position.id'), nullable=False)
    tree_path = Column(String(255), nullable=False, comment='父节点id路径')
    sort = Column(SmallInteger, default=0, comment='显示顺序')

    # 关系
    dept = relationship('Dept', backref='dept_positions')
    position = relationship('Position', backref='dept_positions')
    users = relationship('User', secondary='sys_dept_position_user', back_populates='dept_positions')
    roles = relationship('Role', secondary='sys_dept_position_role', back_populates='dept_positions')

    def __repr__(self):
        return f"<DeptPosition(id={self.id}, name={self.name}, code={self.code})>"