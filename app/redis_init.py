import redis as r

from app.utils.logger_init import logger

from app.config import settings


async def init_redis():
    try:
        redis_client = r.asyncio.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connected.")
        return redis_client
    except r.exceptions.ConnectionError as err:
        logger.error(f"Redis connection error: {err}")
        return None

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    return redis_client
