from app.utils.data_processing_funcs import open_json_file
from app.utils.logger_init import logger
from app.game_data.game_entity_models import GameBoost, get_boosts_registry


async def init_game_boosts(boosts_data: dict = None):
    """
    Создаёт улучшения на основе переданных данных или из JSON-файла и добавляет их в реестр.

    Args:
        boosts_data (dict): Данные улучшений.

    Returns:
        None
    """
    logger.info("Initialization boosts has been launched...")
    if boosts_data is None:
        boosts_data = open_json_file("app/game_data/boosts.json")

    boosts_registry = await get_boosts_registry()
    for boost_name, boost_values in boosts_data.items():
        boost = GameBoost(boost_name, **boost_values)
        boosts_registry.add_entity(boost_name, boost)
    logger.info("Boosts initialize successful.")
