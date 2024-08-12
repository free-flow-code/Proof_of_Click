import ast
from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date

from app.improvements.dao import ImprovementsDAO
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.improvements.processed_functions import (
    get_level_purchased_boost,
    recalculate_user_data,
    get_boost_details
)
from app.redis_init import get_redis
from app.exceptions import (
    AccessDeniedException,
    ObjectNotFoundException,
    BadRequestException,
    NotEnoughFundsException
)

router = APIRouter(
    prefix="/boosts",
    tags=["Boosts"]
)


@router.get("")
async def get_user_boosts(current_user=Depends(get_current_user), redis=Depends(get_redis)):
    user_boosts = await ImprovementsDAO.find_by_user_id(int(current_user["id"]))
    data = {}
    boosts = []
    if user_boosts:
        for user_boost in user_boosts:
            boost = dict(user_boost.items())
            boost[f"{boost['name']}"] = await get_boost_details(
                f"{boost['name']}",
                redis,
                boost_current_lvl=boost["level"]
            )

            keys_to_remove = ["id", "user_id", "name", "purchase_date", "level", "redis_key", "image_id"]
            [boost.pop(key, None) for key in keys_to_remove]
            boosts.append(boost)
    data["boosts"] = boosts

    user_boosts_names = set()
    for boost in data["boosts"]:
        boost_name = tuple(boost.keys())
        user_boosts_names.add(*boost_name)
    all_boosts = await redis.get("name_boosts")
    all_boosts_names = set(ast.literal_eval(all_boosts))
    not_user_boosts_names = all_boosts_names - user_boosts_names

    for boost_name in not_user_boosts_names:
        boost = dict()
        boost[f"{boost_name}"] = await get_boost_details(boost_name, redis)
        data["boosts"].append(boost)

    data["boosts"] = sorted(data["boosts"], key=lambda d: list(d.keys())[0])
    data["user_balance"] = current_user["blocks_balance"]
    data["clicks_per_sec"] = current_user["clicks_per_sec"]
    data["blocks_per_click"] = current_user["blocks_per_click"]
    return data


@router.get("/upgrade/{boost_name}")
async def upgrade_boost(boost_name: str, current_user=Depends(get_current_user), redis=Depends(get_redis)):
    all_boosts = await redis.get("name_boosts")
    if boost_name not in ast.literal_eval(all_boosts):
        raise BadRequestException
    # получить уровень покупаемого улучшения для этого юзера
    level_purchased_boost, boost_id = await get_level_purchased_boost(int(current_user["id"]), boost_name, redis)

    # сравнить стоимость улучшения с текущим балансом юзера, добавить/изменить boost
    boost_value = await redis.get(f"{boost_name}_level_{level_purchased_boost}_value")
    boost_price = await redis.get(f"{boost_name}_level_{level_purchased_boost}_price")
    if float(current_user["blocks_balance"]) >= float(boost_price):
        boost_data = {
            "user_id": int(current_user["id"]),
            "name": boost_name,
            "purchase_date": date.today(),
            "level": level_purchased_boost,
            "redis_key": boost_name
        }
        if not boost_id:
            boost = await ImprovementsDAO.add(**boost_data)
        else:
            boost = await ImprovementsDAO.edit(boost_id, **boost_data)
        # пересчитать blocks_balance, blocks_per_sec, blocks_per_click, boost.level
        await recalculate_user_data(current_user, boost_name, float(boost_price), float(boost_value), redis)
        return boost
    else:
        raise NotEnoughFundsException


@router.get("/buy/{boost_name}")
async def buy_boost(boost_name: str, user: Users = Depends(get_current_user), redis=Depends(get_redis)):
    # TODO
    pass


@router.get("/add_improvement")
async def add_boost(
        user_id: int,
        name: str,
        purchase_date: date,
        level: int,
        redis_key: str,
        image_id: Optional[int] = None,
        current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise AccessDeniedException

    await ImprovementsDAO.add(
        user_id=user_id,
        name=name,
        purchase_date=purchase_date,
        level=level,
        redis_key=redis_key,
        image_id=image_id
    )
    return {"detail": "Boost added successfully"}


@router.delete("/boost/{boost_id}")
async def delete_boost(boost_id: int, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise AccessDeniedException

    item = await ImprovementsDAO.find_one_or_none(id=boost_id)
    if not item:
        raise ObjectNotFoundException

    await ImprovementsDAO.delete(boost_id)
    return {"detail": "Boost deleted successfully"}
