import ast
import logging

from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date

from app.improvements.dao import ImprovementsDAO
from app.improvements.schemas import SImprovements
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.improvements.processed_functions import get_level_purchased_boost, recalculate_user_data
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
async def get_user_boosts(user: Users = Depends(get_current_user)) -> list[SImprovements]:
    return await ImprovementsDAO.find_by_user_id(user.id)


@router.get("buy/{boost_name}")
async def buy_boost(boost_name: str, user: Users = Depends(get_current_user), redis=Depends(get_redis)):
    name_boosts = await redis.get("name_boosts")
    if boost_name not in ast.literal_eval(name_boosts):
        raise BadRequestException
    # получить уровень покупаемого улучшения для этого юзера
    level_purchased_boost, boost_id = await get_level_purchased_boost(user.id, boost_name, redis)

    # сравнить стоимость улучшения с текущим балансом юзера, добавить/изменить boost
    boost_details_str = await redis.get(f"{boost_name}_level_{level_purchased_boost}")
    boost_details = ast.literal_eval(boost_details_str)
    boost_price = boost_details[0]
    if user.blocks_balance >= boost_price:
        boost_data = {
            "user_id": user.id,
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
        await recalculate_user_data(user, boost_name, boost_details)
        return boost
    else:
        raise NotEnoughFundsException


@router.get("/add_improvement")
async def add_boost(
        user_id: int,
        name: str,
        purchase_date: date,
        level: int,
        redis_key: str,
        image_id: Optional[int] = None,
        user: Users = Depends(get_current_user)
):
    if user.role.value != "admin":
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
async def delete_boost(boost_id: int, user: Users = Depends(get_current_user)):
    if user.role.value != "admin":
        raise AccessDeniedException

    item = await ImprovementsDAO.find_one_or_none(id=boost_id)
    if not item:
        raise ObjectNotFoundException

    await ImprovementsDAO.delete(boost_id)
    return {"detail": "Boost deleted successfully"}
