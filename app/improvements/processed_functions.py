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


async def recalculate_user_data(user, boost_name, boost_details):
    updated_user_balance = round(user.blocks_balance - boost_details[0], 3)

    if boost_name == "autoclicker":
        clicks_per_sec = boost_details[1]
        await UsersDAO.edit(user.id, blocks_balance=updated_user_balance, clicks_per_sec=clicks_per_sec)
    elif boost_name == "multiplier":
        blocks_per_click = boost_details[1] / 1000
        await UsersDAO.edit(user.id, blocks_balance=updated_user_balance, blocks_per_click=blocks_per_click)
