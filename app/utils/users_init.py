from typing import Optional, AsyncIterator

from app.users.dao import UsersDAO
from app.utils.logger_init import logger
from app.utils.data_processing_funcs import log_execution_time_async
from app.utils.data_processing_funcs import sanitize_dict_for_redis

from app.config import settings
from app.redis_init import get_redis


async def fetch_all_users_by_key(key: dict, batch_size: int = 100) -> AsyncIterator[list]:
    """
    Генерирует данные по ключу из базы данных пакетами заданного размера.

    Args:
        key (dict): Словарь с параметрами для фильтрации записей.
        batch_size (int): Размер пакета, который будет извлечён за одну итерацию.

    Yields:
        list: Список записей, соответствующих фильтру по ключу, размером не более `batch_size`.

    Notes:
        - Используется пагинация для извлечения всех записей, соответствующих фильтру.
    """
    offset = 0
    while True:
        records = await UsersDAO.fetch_users_by_key(offset=offset, limit=batch_size, **key)
        if not records:
            break
        yield records
        offset += batch_size


async def add_user_data_to_redis(user_data: dict, redis_ttl: Optional[int] = None) -> None:
    """
    Добавляет данные пользователя в Redis.

    Устанавливает время жизни (TTL), если передан соответствующий параметр.

    Args:
        user_data (dict): Словарь с данными пользователя, которые необходимо сохранить.
        redis_ttl (Optional[int]): Время жизни ключа в секундах. Если None, TTL не устанавливается.
    """
    redis_client = await get_redis()
    # await redis_client.zadd(f"users_balances:{settings.node1_tag}", {f"{user_data.get('username')}": user_data.get("blocks_balance", 0.0)})
    # Установить redis_tag по умолчанию, если он не указан
    redis_tag = user_data.get('redis_tag', settings.REDIS_NODE_TAG_1)
    user_id = user_data["id"]
    key = f"user_data:{redis_tag}:{user_id}"

    await redis_client.hset(key, mapping=user_data)

    if redis_ttl is not None:
        current_ttl = await redis_client.ttl(key)
        if current_ttl == -1:  # Если ключ бессрочный
            await redis_client.expire(key, redis_ttl)


@log_execution_time_async
async def add_users_with_autoclicker_to_redis() -> None:
    """
    Загружает данные пользователей с автокликером в Redis.

    Только пользователи, имеющие автокликер (параметр `clicks_per_sec` != 0),
    будут добавлены в Redis на отдельную ноду. Для последуещего подсчета балансов этих пользователей
    с помощью фоновой задачи в Celery.
    """
    logger.info("Adding users with atoclicker to redis has been launched...")
    async for batch in fetch_all_users_by_key(key={"clicks_per_sec": ("!=", 0)}, batch_size=100):
        for record in batch:
            user_data = sanitize_dict_for_redis(record)
            user_data["redis_tag"] = settings.REDIS_NODE_TAG_2
            await add_user_data_to_redis(user_data)
    logger.info("Users with atoclicker loads successful to redis.")


@log_execution_time_async
async def add_top_100_users_to_redis() -> None:
    """
    Загружает топ 100 балансов пользователей в redis из БД.
    """
    logger.info("Adding top 100 users to redis has been launched...")
    redis_client = await get_redis()
    top_users = await UsersDAO.get_top_100_users()
    # for user in top_users:
        # await redis_client.zadd(f"users_balances:{settings.node1_tag}", {f"{user.get('username')}": user.get("blocks_balance", 0.0)})
    logger.info("Top 100 users loads successful to redis.")
