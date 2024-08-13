import logging
import json
from datetime import date

from app.users.models import UserRole
from app.config import settings


async def set_mining_chance(redis_client):
    """Подсчитывает вероятность добычи блока и записывает значение в redis.

    Вероятность это число от 0 до 1, с 4 знаками после запятой.
    Рекомендуется обновлять раз в час.
    """
    users_with_balances = await redis_client.zrange("users_balances", 0, -1, withscores=True)
    total_balance = sum(balance for user, balance in users_with_balances)
    await redis_client.set(
        "mining_chance",
        round((1 - total_balance / settings.MAX_BLOCKS), 4)
    )


def sanitize_dict_for_redis(user_data: dict) -> dict:
    """Заменяет НЕ поддерживаемые в redis типы данных, из значений словаря, на поддерживаемые."""
    return {
        k: (
            v.strftime('%Y-%m-%d') if isinstance(v, date) else
            # add "v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else" for last_update_time
            v.value if isinstance(v, UserRole) else
            str(v) if isinstance(v, bool) else
            str(v) if isinstance(v, list) else
            (v if v is not None else '')
        )
        for k, v in user_data.items()
    }


async def load_boosts(redis_client):
    """Загружает игровые улучшения в redis.

    Все значения находятся в boost:{boost_name}:data и сериализованы с помощью json.dumps.
    """
    name_boosts = []
    with open("app/boosts.json", "r", encoding="utf-8") as file:
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


async def load_game_items(redis_client):
    """Загружает игровые предметы в redis.

    Все значения находятся в game_item:{item_name}. Не сериализованы.
    """
    with open("app/game_items.json", "r", encoding="utf-8") as file:
        game_items = json.loads(file.read())
        for game_item in game_items:
            for item_name, item_details in game_item.items():
                await redis_client.hset(f"game_item:{item_name}", mapping=item_details)
    logging.info("Game items loads successful to redis")
