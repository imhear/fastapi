# app/core/uow.py

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

class AbstractUnitOfWork(ABC):
    """UoW 抽象接口（符合依赖倒置原则）"""
    @abstractmethod
    async def __aenter__(self) -> AsyncSession: ...
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
    @property
    @abstractmethod
    def session(self) -> AsyncSession: ...

class SqlAlchemyUoW(AbstractUnitOfWork):
    """SQLAlchemy UoW 实现（生产级）"""
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._session:
            return
        try:
            if exc_type is None:
                await self._session.commit()  # 无异常则提交
            else:
                await self._session.rollback() # 有异常则回滚
        finally:
            await self._session.close()  # 无论成败都关闭会话
            self._session = None

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise RuntimeError("UoW 未进入上下文（使用 async with）")
        return self._session