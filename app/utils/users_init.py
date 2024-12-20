import json
import numpy as np
from typing import Optional
from itertools import islice
from datetime import datetime
from typing import AsyncIterator

from app.config import settings
from app.users.dao import UsersDAO
from app.redis_init import get_redis
from app.utils.logger_init import logger
from app.tasks.tasks import calculate_items_won_by_list
from app.tasks.tasks import add_items_to_db
from app.utils.game_items_init import get_items_registry
from app.utils.data_processing_funcs import log_execution_time_async
from app.utils.data_processing_funcs import sanitize_dict_for_redis
from app.redis_helpers.lua_scripts import (
    top_users_script,
    recalculate_user_data_script,
    add_user_data_script,
    add_user_balance_script
)


async def calculate_items_won(user_id: int, count_clicks: int, redis_client) -> Optional[int]:
    """
    Подсчитывает количество выпавших игровых предметов для пользователя и обновляет данные в Redis.

    Args:
        user_id (int): Идентификатор пользователя, для которого вычисляются выпавшие предметы.
        count_clicks (int): Количество кликов, совершённых пользователем.
        redis_client: Клиент Redis для взаимодействия с базой данных.

    Returns:
        Optional[int]: Общее количество выпавших предметов или None, если предметы не выпали.

    Notes:
        - Проверяется шанс выпадения для каждого предмета.
        - Если общее количество выпавших предметов превышает максимум, предмет больше не учитывается.
        - Обновления количества предметов и их добавление в базу данных происходят асинхронно.
    """
    item_quantities = await redis_client.hgetall(f"item_quantities:{settings.REDIS_NODE_TAG_1}")
    items_registry = await get_items_registry()
    updates = {}
    total_won = 0

    for item_key, item_details in items_registry.get_all_entities().items():
        # уточняем, количество уже выпавших предметов и его ограничение
        current_quantity = int(item_quantities.get(item_key, 0))
        max_quantity = item_details.get_value("maximum_amount")
        if current_quantity >= max_quantity:
            items_registry.delete_entity(item_key)
            continue

        # вычисляем количество выпавших предметов на основе шанса
        drop_chance = float(item_details.get_value("drop_chance"))
        won_items = np.random.binomial(count_clicks, drop_chance)

        if won_items:
            updates[item_key] = current_quantity + won_items
            total_won += won_items

            add_items_to_db.delay(
                user_id=user_id,
                item_key=item_key,
                items_count=won_items,
                image_id=item_details.get_value("image_id")
            )

    if updates:
        await redis_client.hmset(f"item_quantities:{settings.REDIS_NODE_TAG_1}", updates)

    return total_won


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


async def add_user_data_to_redis(user_data: dict, balance_update: bool = False) -> None:
    """
    Добавляет данные пользователя в Redis.
    Устанавливает время жизни (TTL), в зависимости от наличия автокликера.

    Args:
        user_data (dict): Словарь с данными пользователя, которые необходимо сохранить.
        balance_update (bool): Обновляется баланс или нет.

    Notes:
        Если флаг balance_update == True, то в значение "last_update_time" будет добавлено
        текущее время, в секундах от начала эпохи. Это необходимо для подсчета балансов пользователей
        с автокликером в фоновой задаче.
        Добавление данных происходит на стороне Redis с помощью lua-скриптов.
        Это гарантирует атомарность операций, чтобы избежать состояния гонки при обновлении
        данных из разных мест приложения.
    """
    redis_client = await get_redis()

    ttl = 0
    if not user_data.get("clicks_per_sec"):
        ttl = 3600  # Если пользователь без автокликера, то хранить его данные один час
        user_data['redis_tag'] = settings.REDIS_NODE_TAG_1
    else:
        user_data['redis_tag'] = settings.REDIS_NODE_TAG_2

    user_data_key = f"user_data:{user_data.get('redis_tag')}:{user_data['id']}"
    balances_key = f"users_balances:{settings.REDIS_NODE_TAG_3}"

    if balance_update:
        user_data["last_update_time"] = datetime.now().timestamp()

    add_data_script = redis_client.register_script(add_user_data_script)
    add_balance_script = redis_client.register_script(add_user_balance_script)
    flat_user_data = [str(k) for pair in user_data.items() for k in pair]

    await add_data_script(keys=[user_data_key], args=[ttl, *flat_user_data])
    await add_balance_script(
        keys=[balances_key],
        args=[user_data.get("username"), user_data.get("blocks_balance")]
    )


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
            async with redis_client.pipeline() as pipe:
                for user in records:
                    await pipe.zadd(
                        f"users_balances:{settings.REDIS_NODE_TAG_3}",
                        {f"{user.get('username')}": user.get("blocks_balance", 0.0)}
                    )
                await pipe.execute()
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


@log_execution_time_async
async def recalculate_users_data_in_redis(pattern: str = None, count=100) -> None:
    """
    Пересчитывает балансы пользователей в зависимости от значения автокликера,
    умножителя и времени с последнего обновления.

    Args:
        pattern (str, optional): Шаблон ключей для поиска пользователей в Redis.
                                 По умолчанию используется шаблон для `REDIS_NODE_TAG_2`.
        count (int): Количество пользователей, обрабатываемых за один батч. По умолчанию 100.

    Returns:
        None
    """
    users_keys = set()
    balances_key = f"users_balances:{settings.REDIS_NODE_TAG_3}"
    redis_client = await get_redis()
    if pattern is None:
        pattern = f"user_data:{settings.REDIS_NODE_TAG_2}:*"

    try:
        def get_batches(s, batch_size):
            it = iter(s)
            while True:
                batch = list(islice(it, batch_size))
                if not batch:
                    break
                yield batch

        async for key in redis_client.scan_iter(match=pattern):
            users_keys.add(key)
        script = redis_client.register_script(recalculate_user_data_script)

        for keys_batch in get_batches(users_keys, count):
            current_time = int(datetime.now().timestamp())
            users_clicks = await script(
                keys=keys_batch,
                args=[json.dumps(keys_batch), current_time, balances_key]
            )
            calculate_items_won_by_list.delay(users_clicks, redis_client)
    except Exception as err:
        logger.error(f"Ошибка при пересчете балансов пользователей с автокликером: {err}\n{err.with_traceback()}")
    finally:
        await redis_client.close()
