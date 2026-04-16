
from contextlib import asynccontextmanager
import datetime as dt
from settings import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis



class RedisService:
    def __init__(self):
        global redis
        redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            decode_responses=False,
        )

    @asynccontextmanager
    async def get_redis_client(self):
        try:
            yield self.redis
        finally:
            pass
             # self.redis.close()

    async def set_cash(self, key: str, value: str | int, ttl: int = 60):
        async with self.get_redis_client() as _redis:
            await _redis.setex(key, dt.timedelta(seconds=ttl), value)

    async def get_cash(self, key: str):
        async with self.get_redis_client() as _redis:
            return await _redis.get(key)

    async def delete_cash(self, key: str):
        async with self.get_redis_client() as _redis:
            await _redis.delete(key)

    async def health_check(self) -> tuple[bool, str]:
        try:
            async with self.get_redis_client() as _redis:
                is_alive = await _redis.ping()
            return bool(is_alive), "ok"
        except Exception as exc:
            return False, str(exc)


redis_service = RedisService()
