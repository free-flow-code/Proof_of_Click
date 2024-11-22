import json

from app.utils.logger_init import logger
from app.game_data.game_entity_models import GameBoost, get_boosts_registry


def get_boosts_from_json_file(filepath: str = "app/game_data/boosts.json"):
    with open(filepath, "r", encoding="utf-8") as file:
        boosts_data = json.loads(file.read())
        return boosts_data


async def init_game_boosts(boosts_data: dict = None):
    logger.info("Initialization boosts has been launched...")
    if boosts_data is None:
        boosts_data = get_boosts_from_json_file()

    boosts_registry = await get_boosts_registry()
    for boost_name, boost_values in boosts_data.items():
        boost = GameBoost(boost_name, **boost_values)
        boosts_registry.add_entity(boost_name, boost)
    logger.info("Boosts initialize successful.")
