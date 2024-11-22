import json

from app.utils.logger_init import logger
from app.config import settings
from app.redis_init import get_redis
from app.utils.data_processing_funcs import (
    log_execution_time_async,
    sanitize_dict_for_redis
)
from app.game_data.game_entity_models import GameBoost, get_boosts_registry


@log_execution_time_async
async def add_all_boosts_to_redis():
    """Загружает игровые улучшения в redis.

    Все значения находятся в 'boost:{REDIS_NODE_TAG_1}:{boost_name}: <data>' и сериализованы с помощью json.dumps.
    Список названий всех улучшений в 'name_boosts:{REDIS_NODE_TAG_1}'.
    """
    logger.info("Adding boosts to redis has been launched...")
    redis_client = await get_redis()
    name_boosts = []
    with open("app/game_data/boosts.json", "r", encoding="utf-8") as file:
        boosts = json.loads(file.read())
        for boost in boosts:
            for boost_name, boost_details in boost.items():
                boost_data = {
                    f"{boost_name}": {
                        f"{detail_key}": sanitize_dict_for_redis(detail_data) if detail_key == "levels" else detail_data
                        for detail_key, detail_data in boost_details.items()
                    }
                }
                max_levels = {"max_levels": len(boost_data[f"{boost_name}"]["levels"])}
                boost_data[f"{boost_name}"].update(max_levels)
                name_boosts.append(boost_name)

                # Сериализация словаря в JSON строку перед сохранением в Redis
                serialized_boost_data = json.dumps(boost_data[f"{boost_name}"])
                await redis_client.hset(
                    f"boost:{settings.REDIS_NODE_TAG_1}:{boost_name}",
                    mapping={"data": serialized_boost_data}
                )
    await redis_client.set(f"name_boosts:{settings.REDIS_NODE_TAG_1}", json.dumps(name_boosts))
    logger.info("Boosts loads successful to redis.")


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
