from typing import Optional, AsyncIterator

from app.users.dao import UsersDAO
from app.utils.data_processing_funcs import sanitize_dict_for_redis


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


async def add_user_data_to_redis(user_data: dict, redis_client, redis_ttl: Optional[int] = None) -> None:
    """
    Добавляет данные пользователя в Redis.

    Args:
        user_data (dict): Словарь с данными пользователя, который должен быть сохранён.
        redis_client: Клиент Redis для выполнения операций.
        redis_ttl (int): Время жизни (TTL) для ключа в Redis в секундах. По умолчанию бесконечно.
    """
    await redis_client.zadd("users_balances", {f"{user_data.get('username')}": user_data.get("blocks_balance", 0.0)})
    user_id = user_data.get("id")
    key = f"user_data:{user_id}"
    await redis_client.hset(key, mapping=user_data)

    if redis_ttl is not None:
        current_ttl = await redis_client.ttl(key)
        if current_ttl == -1:  # Если ключ бессрочный
            return
        await redis_client.expire(f"user_data:{user_data['id']}", redis_ttl)


async def add_users_with_autoclicker_to_redis(redis_client) -> None:
    """
    Загружает данные пользователей с автокликером в Redis.

    Только пользователи, имеющие автокликер (параметр `clicks_per_sec` != 0),
    будут добавлены в Redis. Для последуещего подсчета балансов этих пользователей
    с помощью фоновой задачи в Celery.

    Args:
        redis_client: Клиент Redis для выполнения операций.
    """
    async for batch in fetch_all_users_by_key(key={"clicks_per_sec": ("!=", 0)}, batch_size=100):
        for record in batch:
            user_data = sanitize_dict_for_redis(record)
            await add_user_data_to_redis(user_data, redis_client)


async def add_top_100_users_to_redis(redis_client) -> None:
    """
    Загружает топ 100 балансов пользователей в redis из БД.

    Args:
        redis_client: Клиент Redis для выполнения операций.
    """
    top_users = await UsersDAO.get_top_100_users()
    for user in top_users:
        await redis_client.zadd("users_balances", {f"{user.get('username')}": user.get("blocks_balance", 0.0)})
