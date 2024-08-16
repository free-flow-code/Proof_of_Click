import ast
import json
from app.improvements.dao import ImprovementsDAO
from app.exceptions import BadRequestException


async def get_level_purchased_boost(user_id: int, boost_name: str, redis_client):
    user_boost = await ImprovementsDAO.get_user_boost_by_name(user_id, boost_name)
    boost_details = await redis_client.hgetall(f"boost:{boost_name}")
    boost_max_levels = boost_details["data"]["max_levels"]

    if not user_boost:
        level_purchased_boost = 1
        boost_id = None
        return level_purchased_boost, boost_id
    elif user_boost.level < int(boost_max_levels):
        level_purchased_boost = user_boost.level + 1
        boost_id = user_boost.id
        return level_purchased_boost, boost_id
    else:
        raise BadRequestException


async def recalculate_user_data(user: dict, boost_name: str, boost_price: float, boost_value: int, redis):
    updated_user_balance = round(float(user["blocks_balance"]) - boost_price, 3)
    await redis.zadd("users_balances", {f"{user['username']}": updated_user_balance})

    if boost_name == "autoclicker":
        await redis.hset(f"user_data:{user['id']}", mapping={"clicks_per_sec": boost_value})
    elif boost_name == "multiplier":
        await redis.hset(f"user_data:{user['id']}", mapping={"blocks_per_click": boost_value})


async def get_boost_details(boost_name: str, redis, boost_current_lvl=0, language="en"):
    boost = await redis.hgetall(f"boost:{boost_name}")
    boost_details = json.loads(boost["data"])

    if not boost_current_lvl:
        boost_current_value = 0
    else:
        boost_current_value = ast.literal_eval(boost_details["levels"][f"{boost_current_lvl}"])[1]

    boost_max_levels = boost_details["max_levels"]
    boost_max_value = ast.literal_eval(boost_details["levels"][f"{boost_max_levels}"])[1]
    usdt_price = boost_details["usdt_price"]

    if boost_current_lvl == boost_max_levels:
        boost_next_lvl_value = None
        boost_next_lvl_price = None
    else:
        boost_next_lvl_details = ast.literal_eval(boost_details["levels"][f"{boost_current_lvl + 1}"])
        boost_next_lvl_value = boost_next_lvl_details[1]
        boost_next_lvl_price = boost_next_lvl_details[0]

    return {
        "current_level": boost_current_lvl,
        "image_id": boost_details["image_id"],
        "boost_title": boost_details[f"name_{language}"],
        "description": boost_details[f"description_{language}"],
        "characteristic": boost_details[f"characteristic_{language}"],
        "current_value": boost_current_value,
        "max_value": boost_max_value,
        "next_lvl_value": boost_next_lvl_value,
        "next_lvl_price": boost_next_lvl_price,
        "usdt_price": usdt_price
    }
