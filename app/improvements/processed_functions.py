from app.improvements.dao import ImprovementsDAO
from app.users.dao import UsersDAO
from app.exceptions import BadRequestException


async def get_level_purchased_boost(user_id, boost_name, redis):
    user_boost = await ImprovementsDAO.get_user_boost_by_name(user_id, boost_name)
    boost_max_levels = await redis.get(f"{boost_name}_max_levels")

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


async def recalculate_user_data(user, boost_name, boost_value):
    updated_user_balance = round(user.blocks_balance - boost_value, 3)

    if boost_name == "autoclicker":
        clicks_per_sec = boost_value
        await UsersDAO.edit(user.id, blocks_balance=updated_user_balance, clicks_per_sec=clicks_per_sec)
    elif boost_name == "multiplier":
        blocks_per_click = boost_value
        await UsersDAO.edit(user.id, blocks_balance=updated_user_balance, blocks_per_click=blocks_per_click)


async def get_boost_details(boost_name, redis, boost_current_lvl=0, language="en"):
    boost_title = await redis.get(f"{boost_name}_name_{language}")
    description = await redis.get(f"{boost_name}_description_{language}")
    characteristic = await redis.get(f"{boost_name}_characteristic_{language}")
    image_id = await redis.get(f"{boost_name}_image_id")

    boost_current_value = await redis.get(f"{boost_name}_level_{boost_current_lvl}_value")

    boost_max_levels = await redis.get(f"{boost_name}_max_levels")
    boost_max_value = await redis.get(f"{boost_name}_level_{boost_max_levels}_value")
    usdt_price = await redis.get(f"{boost_name}_usdt_price")

    if boost_current_lvl == boost_max_levels:
        boost_next_lvl_value = None
        boost_next_lvl_price = None
    else:
        boost_next_lvl_value = await redis.get(f"{boost_name}_level_{boost_current_lvl + 1}_value")
        boost_next_lvl_price = await redis.get(f"{boost_name}_level_{boost_current_lvl + 1}_price")

    return {
        "current_level": boost_current_lvl,
        "image_id": image_id,
        "boost_title": boost_title,
        "description": description,
        "characteristic": characteristic,
        "current_value": boost_current_value,
        "max_value": boost_max_value,
        "next_lvl_value": boost_next_lvl_value,
        "next_lvl_price": boost_next_lvl_price,
        "usdt_price": usdt_price
    }
