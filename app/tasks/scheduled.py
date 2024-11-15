import asyncio
from celery import shared_task

from app.redis_init import get_redis
from app.utils.data_processing_funcs import set_mining_chance


@shared_task(name="set_mining_chance")
def set_mining_chance():
    """Пересчитать и записать в redis новое значение для mining_chance."""
    redis_client = asyncio.run(get_redis())
    asyncio.run(set_mining_chance(redis_client))
