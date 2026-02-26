# app/services/redis_service.py
import redis.asyncio as redis


class RedisService:
    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client

    async def set_value(self, key: str, value: str):
        await self.client.set(key, value)

    async def get_value(self, key: str) -> str:
        return await self.client.get(key)