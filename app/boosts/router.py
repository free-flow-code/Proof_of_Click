import ast
import json
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends

from app.config import settings
from app.redis_init import get_redis
from app.boosts.dao import ImprovementsDAO
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.utils.boosts_init import get_boosts_registry
from app.boosts.processed_functions import (
    get_level_purchased_boost,
    recalculate_user_data_in_dbs,
    get_boost_details
)
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
async def get_user_boosts(language: str = "en", current_user=Depends(get_current_user)) -> dict:
    """
    Возвращает информацию о всех улучшениях пользователя, включая приобретённые и доступные для покупки.

    Args:
        language (str): Язык описания бустов.
        current_user: Текущий пользователь.

    Returns:
        dict: Словарь с данными по улучшениям пользователя, включающий:
            - boosts (list): Список словарей с информацией по каждому улучшению:
                - Где ключи словарей - названия улучшений, а значения - их характеристики.
                - Для приобретённых улучшений включены текущие характеристики и уровень.
                - Для доступных улучшений включены базовые характеристики.
    """
    user_boosts = await ImprovementsDAO.find_by_user_id(int(current_user["id"]))
    boosts_registry = await get_boosts_registry()
    user_boosts_names = []
    summary_data = {}
    boosts = []

    # Получаем данные для текущего уровня улучшений пользователя
    if user_boosts:
        for user_boost in user_boosts:
            boost = {
                user_boost.name: await get_boost_details(
                    boosts_registry,
                    user_boost.name,
                    boost_current_lvl=user_boost.level,
                    language=language
                )
            }
            user_boosts_names.append(user_boost.name)
            boosts.append(boost)

    summary_data["boosts"] = boosts

    all_boosts_in_game = boosts_registry.get_all_entities().keys()
    not_user_boosts_names = all_boosts_in_game - user_boosts_names

    # Получаем данные для улучшений, которых нет у пользователя
    for boost_name in not_user_boosts_names:
        boost = {
            boost_name: await get_boost_details(boosts_registry, boost_name, language=language)
        }
        summary_data["boosts"].append(boost)

    summary_data["boosts"] = sorted(summary_data["boosts"], key=lambda d: list(d.keys())[0])
    return summary_data


@router.get("/upgrade/{boost_name}")
async def upgrade_boost(
        boost_name: str,
        current_user=Depends(get_current_user),
        redis_client=Depends(get_redis)
) -> dict:
    """
    Покупка улучшения за игровую валюту (blocks).
    Повышает уровень улучшения для пользователя, если достаточно средств на балансе.
    Обновляет значения характеристик и баланса, соответственно купленному улучшению.

    Args:
        boost_name (str): Название улучшения, которое нужно приобрести или улучшить.
        current_user: Текущий пользователь.
        redis_client: Клиент Redis, для выполнения асинхронных операций.

    Returns:
        dict: Словарь с данными о прокаченном улучшении, включающий:
            - name (str): Название улучшения,
            - level (int): Уровень улучшения,
            - image_id (int): id изображения, None - если нет

    Raises:
        BadRequestException: Если указанное улучшение не существует.
        NotEnoughFundsException: Если средств на балансе пользователя недостаточно для покупки.
    """
    all_boosts = await redis_client.get(f"name_boosts:{settings.REDIS_NODE_TAG_1}")
    if boost_name not in ast.literal_eval(all_boosts):
        raise BadRequestException

    boost = await redis_client.hgetall(f"boost:{settings.REDIS_NODE_TAG_1}:{boost_name}")
    boost_details = json.loads(boost["data"])
    user_id = int(current_user["id"])
    # получить уровень и характеристики ПОКУПАЕМОГО улучшения для этого юзера
    level_purchased_boost, boost_id = await get_level_purchased_boost(user_id, boost_name, boost_details)
    boost_level_details = ast.literal_eval(
        boost_details["levels"][f"{level_purchased_boost}"]
    )
    boost_value = boost_level_details[1]
    boost_price = float(boost_level_details[0])
    # сравнить стоимость улучшения с текущим балансом юзера
    if float(current_user["blocks_balance"]) >= boost_price:
        boost_data = {
            "user_id": user_id,
            "name": boost_name,
            "purchase_date": date.today(),
            "level": level_purchased_boost,
            "redis_key": boost_name
        }
        # добавить/изменить boost в базе
        if not boost_id:
            boost = await ImprovementsDAO.add(**boost_data)
        else:
            boost = await ImprovementsDAO.edit(boost_id, **boost_data)
        # пересчитать в Redis blocks_balance, clicks_per_sec, blocks_per_click
        await recalculate_user_data_in_dbs(current_user, boost_name, boost_price, boost_value)

        boost_data = dict(boost)
        keys_to_remove = ["id", "user_id", "purchase_date", "redis_key"]
        [boost_data.pop(key, None) for key in keys_to_remove]
        return boost_data
    else:
        raise NotEnoughFundsException


@router.get("/buy/{boost_name}")
async def buy_boost(boost_name: str, user: Users = Depends(get_current_user), redis=Depends(get_redis)):
    """Покупка улучшения за USDT."""
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
    """
    Добавляет новое улучшение для пользователя. Доступно только для администратора.

    Args:
        user_id (int): Идентификатор пользователя, для которого добавляется улучшение.
        name (str): Название улучшения.
        purchase_date (date): Дата покупки улучшения.
        level (int): Уровень улучшения.
        redis_key (str): Ключ в Redis, связанный с улучшением.
        image_id (Optional[int], optional): Идентификатор изображения улучшения. По умолчанию None.
        current_user: Текущий пользователь.

    Returns:
        dict: Содержит сообщение о результате добавления улучшения.

    Raises:
        AccessDeniedException: Если текущий пользователь не имеет прав администратора.
    """
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
    """
    Удаляет улучшение по его идентификатору. Доступно только для администратора.

    Args:
        boost_id (int): Идентификатор удаляемого улучшения.
        current_user: Текущий пользователь.

    Returns:
        dict: Содержит сообщение о результате удаления улучшения.

    Raises:
        AccessDeniedException: Если текущий пользователь не имеет прав администратора.
        ObjectNotFoundException: Если улучшение с указанным идентификатором не найдено.
    """
    if current_user["role"] != "admin":
        raise AccessDeniedException

    item = await ImprovementsDAO.find_one_or_none(id=boost_id)
    if not item:
        raise ObjectNotFoundException

    await ImprovementsDAO.delete(boost_id)
    return {"detail": "Boost deleted successfully"}
