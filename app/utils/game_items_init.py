from app.utils.data_processing_funcs import open_json_file
from app.utils.logger_init import logger
from app.config import settings
from app.redis_init import get_redis
from app.boosts.dao import ImprovementsDAO
from app.game_data.game_entity_models import GameItem, get_items_registry


async def get_items_quantity_from_db(item_keys: list[str]) -> dict:
    """
    Получает количество записей из таблицы игровых предметов по ключам в списке.

    Args:
        item_keys (list): Список ключей (названия игровых предметов).

    Returns:
        dict: Словарь вида <ключ>: <количество записей>
    """
    items_data = {}
    for item_key in item_keys:
        item_quantity = await ImprovementsDAO.count_records_by_key(name=item_key)
        items_data[item_key] = item_quantity
    return items_data


async def set_items_quantity_in_redis() -> None:
    """
    Устанавливает начальное количество для каждого игрового предмета в Redis.
    """
    redis_client = await get_redis()
    items_registry = await get_items_registry()
    item_keys = list(items_registry.get_all_entities().keys())
    items_data = await get_items_quantity_from_db(item_keys)

    async with redis_client.pipeline() as pipe:
        for item_name, quantity in items_data.items():
            await pipe.hset(f"item_quantities:{settings.REDIS_NODE_TAG_1}", item_name, quantity)
        await pipe.execute()


async def init_game_items(items_data: dict = None) -> None:
    """
    Создаёт игровые предметы на основе переданных данных или из JSON-файла и добавляет их в реестр.

    Args:
        items_data (dict): Данные игровых предметов.

    Returns:
        None
    """
    logger.info("Creating game items has been launched...")
    if items_data is None:
        items_data = open_json_file("app/game_data/game_items.json")
    try:
        game_items_registry = await get_items_registry()
        for boost_name, boost_values in items_data.items():
            boost = GameItem(boost_name, **boost_values)
            game_items_registry.add_entity(boost_name, boost)
        logger.info("Game items create successful.")
    except Exception as err:
        logger.error(f"{err}")
