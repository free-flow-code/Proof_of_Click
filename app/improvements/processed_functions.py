import ast
import json
from app.users.dao import UsersDAO
from app.improvements.dao import ImprovementsDAO
from app.exceptions import BadRequestException
from app.utils.users_init import add_user_data_to_redis

from app.utils.data_processing_funcs import restore_types_from_redis


async def get_level_purchased_boost(user_id: int, boost_name: str, redis_client):
    """
    Получает уровень, до которого прокачается покупаемое пользователем улучшение (если он его покупал),
     и возвращает его вместе с идентификатором улучшения.

    Args:
        user_id (int): Идентификатор пользователя.
        boost_name (str): Название улучшения.
        redis_client: Клиент Redis для выполнения асинхронных операций.

    Returns:
        tuple: Кортеж, содержащий:
            - level_purchased_boost (int): Уровень покупаемого улучшения.
            - boost_id (int, None): Идентификатор улучшения или None, если улучшение ещё не приобреталось.

    Raises:
        BadRequestException: Если текущий уровень улучшения пользователя достиг максимального.
    """
    user_boost = await ImprovementsDAO.get_user_boost_by_name(user_id, boost_name)
    boost = await redis_client.hgetall(f"boost:{boost_name}")
    boost_details = json.loads(boost["data"])
    boost_max_levels = boost_details["max_levels"]

    if not user_boost:
        level_purchased_boost = 1
        boost_id = None
        return level_purchased_boost, boost_id
    elif user_boost.level < boost_max_levels:
        level_purchased_boost = user_boost.level + 1
        boost_id = user_boost.id
        return level_purchased_boost, boost_id
    else:
        raise BadRequestException


async def recalculate_user_data_in_dbs(
        current_user: dict,
        boost_name: str,
        boost_price: float,
        boost_value: str,
        redis_client
) -> None:
    """
    Обновляет в Redis и базе значения баланса и улучшений пользователя в зависимости от купленного им улучшения.

    Args:
        current_user (dict): Словарь с данными пользователя, включая `id`, `username` и `blocks_balance`.
        boost_name (str): Название купленного улучшения.
        boost_price (float): Цена улучшения.
        boost_value (int): Значение улучшения, устанавливаемое для соответствующего параметра пользователя.
        redis_client: Клиент Redis для выполнения асинхронных операций.

    Returns:
        None

    Notes:
        - Если пользователь покупает не автокликер и у него еще нет автокликера, то время хранения
          его данных в Redis - 1 час. Иначе - бесконечно. Это нужно для подсчета баланса в фоне.
    """
    redis_ttl = None
    if boost_name.lower() != "autoclicker" and not current_user["clicks_per_sec"]:
        redis_ttl = 3600

    if boost_name.lower() == "autoclicker":
        current_user["clicks_per_sec"] = int(boost_value)
    elif boost_name.lower() == "multiplier":
        current_user["blocks_per_click"] = float(boost_value)

    current_user["blocks_balance"] = round(float(current_user["blocks_balance"]) - boost_price, 3)
    await add_user_data_to_redis(current_user, redis_client, redis_ttl)
    
    deserialized_data = restore_types_from_redis(current_user)
    await UsersDAO.edit(int(current_user["id"]), **deserialized_data)


async def get_boost_details(boost_name: str, redis, boost_current_lvl=0, language="en") -> dict:
    """
    Получает характеристики для заданного улучшения из Redis.

    Args:
        boost_name (str): Название улучшения, используемое для поиска данных в Redis.
        redis: Клиент Redis для выполнения асинхронных операций.
        boost_current_lvl (int, optional): Текущий уровень улучшения. По умолчанию 0.
        language (str, optional): Язык для отображения данных улучшения. По умолчанию "en".

    Returns:
        dict: Словарь с характеристиками улучшения, включающий:
            - current_level (int): Текущий уровень улучшения.
            - image_id (str): Идентификатор изображения улучшения.
            - boost_title (str): Название улучшения на выбранном языке.
            - description (str): Описание улучшения на выбранном языке.
            - characteristic (str): Название улучшаемого параметра на выбранном языке.
            - current_value (float): Текущее значение улучшения.
            - max_value (float): Максимальное значение улучшения.
            - next_lvl_value (float, None): Значение улучшения на следующем уровне или None,
            если достигнут максимальный уровень.
            - next_lvl_price (float, None): Цена улучшения для следующего уровня или None,
            если достигнут максимальный уровень.
            - usdt_price (float): Цена улучшения в USDT.
    """
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
