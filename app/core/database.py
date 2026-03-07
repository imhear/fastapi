from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

from sqlalchemy import Column, func, DateTime, SmallInteger, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "local",
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

class BaseTableModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    create_time = Column(DateTime, server_default=func.now(), nullable=False)
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(SmallInteger, default=0, comment='逻辑删除标识(0-未删除 1-已删除)')
    status = Column(SmallInteger, default=1, comment='状态(1-正常 0-禁用)')

    # 审计字段
    create_by = Column(UUID(as_uuid=True), nullable=True, comment='创建人ID')
    update_by = Column(UUID(as_uuid=True), nullable=True, comment='最后更新人ID')

    # ... 其他字段 ...
    version = Column(Integer, default=1, nullable=False, comment='乐观锁版本号')

def datetime_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"无法序列化类型：{type(obj)}")

async def get_async_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()   # 无异常时提交
        except Exception:
            await session.rollback()  # 有异常时回滚
            raise
        finally:
            await session.close()