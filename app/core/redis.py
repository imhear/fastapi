import redis.asyncio as redis
from app.core.config import settings


async def get_redis_client() -> redis.Redis:
    """FastAPI 依赖：提供请求级 Redis 客户端"""
    client = redis.from_url(
        settings.REDIS_URL,
        encoding=settings.REDIS_ENCODING,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        socket_keepalive=True,
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
        socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
    )
    try:
        yield client
    finally:
        await client.close()