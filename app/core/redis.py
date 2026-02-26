# app/core/redis.py
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
#
# # app/core/redis.py（完整的Redis客户端创建函数）
# import redis.asyncio as redis
# from app.core.config import settings
#
# def get_redis_client() -> redis.Redis:
#     """创建并返回Redis异步客户端（单例）"""
#     try:
#         client = redis.Redis(
#             host="localhost",
#             port=6379,
#             db=0,
#             password="",
#             encoding="utf-8",
#             decode_responses=True,
#             # 连接超时配置
#             socket_connect_timeout=5,
#             socket_timeout=5,
#         )
#         return client
#     except Exception as e:
#         raise RuntimeError(f"Redis客户端初始化失败: {str(e)}") from e