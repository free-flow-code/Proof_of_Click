import redis as r
import logging

from app.config import settings


async def add_user_data_to_redis(user_data: dict):
    redis_client = await get_redis()
    await redis_client.zadd("users_balances", {f"{user_data.get('username')}": user_data.get("blocks_balance", 0.0)})
    user_id = user_data.get("id")
    await redis_client.hset(f"user_data:{user_id}", mapping=user_data)
    await redis_client.expire(f"user_data:{user_id}", 3600)


async def init_redis():
    try:
        redis_client = r.asyncio.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf8",
            decode_responses=True
        )
        await redis_client.ping()
        logging.info("Redis connected.")
        return redis_client
    except r.exceptions.ConnectionError as err:
        logging.error(f"Redis connection error: {err}")
        return None

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    return redis_client
