"""
数据库会话+系统通用建表模型
app/core/database.py
"""
from datetime import datetime
from app.config.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import Column, func, DateTime, SmallInteger, Integer, BigInteger

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "local",
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
)

# 异步会话工厂
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)

# 数据库依赖项
async def get_async_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()   # 无异常时提交
        except Exception:
            await session.rollback()  # 有异常时回滚
            raise

# 日志专用独立会话工厂（系统日志/错误日志）
log_async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
)

LogAsyncSessionLocal = async_sessionmaker(
    bind=log_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 日志会话获取函数（供外部显式调用）
async def create_log_session() -> AsyncSession:
    """创建日志专用会话（外部显式调用）"""
    session = LogAsyncSessionLocal()
    return session


# 基础模型
Base = declarative_base()


class BaseTableModel(Base):
    __abstract__ = True

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 软删除&状态
    is_deleted = Column(SmallInteger, default=0, comment='逻辑删除标识(0-未删除 1-已删除)')
    status = Column(SmallInteger, default=1, comment='状态(1-正常 0-禁用)')

    # 审计字段
    create_by = Column(BigInteger, nullable=True, comment='创建人ID')
    update_by = Column(BigInteger, nullable=True, comment='最后更新人ID')
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment='创建时间')
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment='更新时间')
    delete_by = Column(BigInteger, nullable=True, comment='删除人ID')
    delete_time = Column(DateTime(timezone=True), nullable=True, comment='删除时间')
    # 多租户预留
    tenant_id = Column(BigInteger, default=1, nullable=False, comment='租户ID（默认1为系统租户）')

    # 乐观锁
    version = Column(Integer, default=1, nullable=False, comment='乐观锁版本号')
    # 乐观锁配置
    __mapper_args__ = {
        "version_id_col": version,
        "version_id_generator": lambda v: (v or 0) + 1  # 明确版本号自增逻辑
    }

# 时间序列化工具
def datetime_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"无法序列化类型：{type(obj)}")


__all__ = ['get_async_db', 'create_log_session', 'Base', 'BaseTableModel', 'datetime_encoder']
