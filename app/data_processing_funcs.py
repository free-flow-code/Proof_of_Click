import logging
import json
from datetime import date

from app.users.models import UserRole
from  app.config import settings


async def calculate_chance_mining_block(redis_client):
    """Подсчитывает вероятность добычи блока и записывает значение в redis.
    Вероятность это число от 0 до 1, с 4 знаками после запятой.
    Рекомендуется обновлять раз в час."""
    users_with_balances = await redis_client.zrange("users_balances", 0, -1, withscores=True)
    total_balance = sum(balance for user, balance in users_with_balances)
    await redis_client.set(
        "mining_chance",
        round((1 - total_balance / settings.MAX_BLOCKS), 4)
    )


def sanitize_user_data(user_data):
    return {
        k: (
            v.strftime('%Y-%m-%d') if isinstance(v, date) else
            # add "v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else" for last_update_time
            v.value if isinstance(v, UserRole) else
            str(v) if isinstance(v, bool) else
            (v if v is not None else '')
        )
        for k, v in user_data.items()
    }


async def load_boosts(redis):
    pipe = redis.pipeline()
    name_boosts = []
    with open("app/boosts.json", "r", encoding="utf-8") as file:
        boosts = json.loads(file.read())
        for boost in boosts:
            for key, value in boost.items():
                name_boosts.append(key)
                pipe.set(f"{key}_name_ru", value["name_ru"])
                pipe.set(f"{key}_name_en", value["name_en"])
                pipe.set(f"{key}_description_ru", value["description_ru"])
                pipe.set(f"{key}_description_en", value["description_en"])
                pipe.set(f"{key}_characteristic_ru", value["characteristic_ru"])
                pipe.set(f"{key}_characteristic_en", value["characteristic_en"])
                pipe.set(f"{key}_usdt_price", value["usdt_price"])
                pipe.set(f"{key}_image_id", value["image_id"])
                levels_count = 0
                for level, details in value["levels"].items():
                    pipe.set(f"{key}_level_{level}_price", details[0])
                    pipe.set(f"{key}_level_{level}_value", details[1])
                    levels_count += 1
                pipe.set(f"{key}_max_levels", levels_count)
    pipe.set("name_boosts", str(name_boosts))
    await pipe.execute()
    logging.info("Boosts loads successful to redis")


async def load_game_items(redis):
    pipe = redis.pipeline()
    with open("app/game_items.json", "r", encoding="utf-8") as file:
        game_items = json.loads(file.read())
        for game_item in game_items:
            for key, value in game_item.items():
                pipe.set(f"{key}_name_ru", value["name_ru"])
                pipe.set(f"{key}_name_en", value["name_en"])
                pipe.set(f"{key}_description_ru", value["description_ru"])
                pipe.set(f"{key}_description_en", value["description_en"])
                pipe.set(f"{key}_mining_probability", value["mining_probability"])
                pipe.set(f"{key}_maximum_amount", value["maximum_amount"])
    await pipe.execute()
    logging.info("Game items loads successful to redis")
