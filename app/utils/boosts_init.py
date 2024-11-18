import logging
import json

from app.utils.data_processing_funcs import sanitize_dict_for_redis


async def add_all_boosts_to_redis(redis_client):
    """Загружает игровые улучшения в redis.

    Все значения находятся в 'boost:{boost_name}: <data>' и сериализованы с помощью json.dumps.
    Список названий всех улучшений в 'name_boosts'.
    """
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
                await redis_client.hset(f"boost:{boost_name}", mapping={"data": serialized_boost_data})
    await redis_client.set("name_boosts", json.dumps(name_boosts))
    logging.info("Boosts loads successful to redis")
