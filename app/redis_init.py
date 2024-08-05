import redis
import logging
from app.config import settings


async def init_redis():
    try:
        redis_client = redis.asyncio.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf8",
            decode_responses=True
        )
        await redis_client.ping()
        logging.info("Redis connected.")
        return redis_client
    except redis.exceptions.ConnectionError as err:
        logging.error(f"Redis connection error: {err}")
        return None

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    return redis_client
