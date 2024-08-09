import json
import redis as r
import logging
from app.config import settings


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


async def init_redis():
    try:
        redis_client = r.asyncio.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf8",
            decode_responses=True
        )
        await redis_client.ping()
        logging.info("Redis connected.")
        return redis_client
    except r.exceptions.ConnectionError as err:
        logging.error(f"Redis connection error: {err}")
        return None

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    return redis_client
