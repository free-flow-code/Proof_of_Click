from typing import Optional, AsyncIterator

from app.config import settings
from app.users.dao import UsersDAO
from app.redis_init import get_redis
from app.utils.logger_init import logger
from app.redis_helpers.lua_scripts import top_users_script
from app.utils.data_processing_funcs import log_execution_time_async
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


async def add_user_data_to_redis(user_data: dict, redis_ttl: Optional[int] = None) -> None:
    """
    Добавляет данные пользователя в Redis.

    Устанавливает время жизни (TTL), если передан соответствующий параметр.

    Args:
        user_data (dict): Словарь с данными пользователя, которые необходимо сохранить.
        redis_ttl (Optional[int]): Время жизни ключа в секундах. Если None, TTL не устанавливается.
    """
    redis_client = await get_redis()
    # Обновить баланс
    await redis_client.zadd(
        f"users_balances:{settings.REDIS_NODE_TAG_3}",
        {f"{user_data.get('username')}": user_data.get("blocks_balance", 0.0)}
    )
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
async def add_all_users_balances_to_redis(batch_size: int = 100) -> None:
    """
    Загружает балансы всех пользователей в redis из БД.
    Для дальнейшего подсчета mining_chance и составления таблицы лидеров.
    """
    redis_client = await get_redis()
    if not await redis_client.exists(f"users_balances:{settings.REDIS_NODE_TAG_3}"):
        logger.info("Adding all users balances to redis has been launched...")

        offset = 0
        while True:
            records = await UsersDAO.find_all(offset=offset, limit=batch_size)
            if not records:
                break
            for user in records:
                await redis_client.zadd(
                    f"users_balances:{settings.REDIS_NODE_TAG_3}",
                    {f"{user.get('username')}": user.get("blocks_balance", 0.0)}
                )
                offset += batch_size
        logger.info("All users balances loads successful to redis.")


async def get_top_users(top_n: int, zset_key: str, redis_client) -> list[list[str, str]]:
    """
    Получает топ N пользователей из Redis ZSET с использованием скрипта Lua.

    Args:
        top_n (int): Количество пользователей, которых нужно выбрать.
        zset_key (str): Ключ ZSET в Redis, содержащий данные пользователей.
        redis_client: Клиент для взаимодействия с Redis.

    Returns:
        list[list[str, str]]: Список списков, где каждый элемент содержит имя пользователя и его баланс.
    """
    script = redis_client.register_script(top_users_script)
    result = await script(keys=[zset_key], args=[top_n])
    return result


async def get_top_100_users() -> dict:
    """
    Получает топ-100 пользователей с их балансами из Redis.

    Returns:
        dict: Словарь, где ключи — это имена пользователей, а значения — их балансы.
    """
    redis_client = await get_redis()
    key = f"users_balances:{settings.REDIS_NODE_TAG_3}"

    top_users = {}
    if await redis_client.exists(f"{key}"):
        users = await get_top_users(100, key, redis_client)
        top_users = {}

        for user in users:
            username = user[0]
            balance = float(user[1])
            top_users[username] = balance

    return top_users


async def add_top_100_users_to_redis(top_users: dict = None) -> None:
    """
    Добавляет топ-100 пользователей с их балансами в Redis с временем жизни ключа в 10 секунд.

    Args:
        top_users (dict): Словарь, где ключи — это имена пользователей, а значения — их балансы.

    Returns:
        None
    """
    redis_client = await get_redis()

    if top_users is None:
        top_users = await get_top_100_users()

    await redis_client.hset(
        f"top_100:{settings.REDIS_NODE_TAG_3}",
        mapping=top_users
    )
    await redis_client.expire(f"top_100:{settings.REDIS_NODE_TAG_3}", 10)
