# app/modules/log/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from .models import BusinessLog

class LogRepository:
    async def create(self, session: AsyncSession, log_data: dict) -> None:
        log = BusinessLog(**log_data)
        session.add(log)
        await session.flush()   # 不提交，由外部事务统一控制