from redis import asyncio as aioredis
from app.config import settings

redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf8",
    decode_responses=True
)


async def get_redis():
    return redis
