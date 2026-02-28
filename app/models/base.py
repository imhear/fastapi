# app/models/base.py
import uuid
from sqlalchemy import Column, func, DateTime, SmallInteger, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# def uuid_pk_column() -> Column:
#     return Column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#         server_default=func.gen_random_uuid(),
#         comment="主键UUID",
#     )


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    create_time = Column(DateTime, server_default=func.now(), nullable=False)
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(SmallInteger, default=0, comment='逻辑删除标识(0-未删除 1-已删除)')
    status = Column(SmallInteger, default=1, comment='状态(1-正常 0-禁用)')

    # 审计字段
    create_by = Column(UUID(as_uuid=True), nullable=True, comment='创建人ID')
    update_by = Column(UUID(as_uuid=True), nullable=True, comment='最后更新人ID')

    # ... 其他字段 ...
    version = Column(Integer, default=1, nullable=False, comment='乐观锁版本号')