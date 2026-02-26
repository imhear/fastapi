from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "local",
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
)

AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_db() -> AsyncSession:
    """FastAPI 依赖：提供请求级会话，每次请求创建一个会话，请求结束后关闭"""
    async with AsyncSessionFactory() as session:
        yield session