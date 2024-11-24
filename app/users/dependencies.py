from fastapi import Depends, Request
from jose import jwt, JWTError
from datetime import datetime
from typing import Optional

from app.config import settings
from app.users.dao import UsersDAO
from app.redis_init import get_redis
from app.utils.data_processing_funcs import sanitize_dict_for_redis
from app.utils.users_init import add_user_data_to_redis
from app.exceptions import (
    TokenExpiredException,
    TokenAbsentException,
    IncorrectTokenFormatException,
    UserIsNotPresentException
)


def get_token(request: Request):
    token = request.cookies.get("poc_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_user_data_from_redis(user_id: int) -> Optional[dict]:
    """
    Получает данные пользователя из Redis.

    Последовательно проверяет две ноды Redis (определенные через теги)
    и возвращает данные, если они найдены. Добавляет ключ `redis_tag` в словарь
    для указания, с какой ноды были получены данные.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        Optional[dict]: Словарь с данными пользователя и ключом `redis_tag`,
                        либо None, если пользователь не найден.
    """
    redis_client = await get_redis()

    # Проверка первой ноды
    user_data = await redis_client.hgetall(f"user_data:{settings.REDIS_NODE_TAG_1}:{user_id}")
    if user_data:
        user_data["redis_tag"] = settings.REDIS_NODE_TAG_1
        return user_data

    # Проверка второй ноды
    user_data = await redis_client.hgetall(f"user_data:{settings.REDIS_NODE_TAG_2}:{user_id}")
    if user_data:
        user_data["redis_tag"] = settings.REDIS_NODE_TAG_2
        return user_data

    # Данные пользователя не найдены
    return None


async def get_current_user(token: str = Depends(get_token)) -> dict:
    """
    Извлекает текущего пользователя на основе переданного JWT-токена.

    Args:
        token (str): JWT-токен, извлекаемый из заголовков запроса.

    Returns:
        dict: Словарь с данными пользователя, извлечённый из Redis или базы данных.

    Raises:
        IncorrectTokenFormatException: Если формат токена некорректен или его невозможно декодировать.
        TokenExpiredException: Если срок действия токена истёк.
        UserIsNotPresentException: Если пользователь не найден в базе данных.

    Notes:
        - Проверяет срок действия токена и достаёт идентификатор пользователя из его payload.
        - Если данные пользователя отсутствуют в Redis, они извлекаются из базы данных,
          форматируются и сохраняются в Redis для последующего использования.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise IncorrectTokenFormatException

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException
    user_id = int(payload.get("sub"))
    if not user_id:
        raise UserIsNotPresentException

    user_data = await get_user_data_from_redis(user_id)
    if not user_data:
        user = await UsersDAO.find_by_model_id(user_id)
        if not user:
            raise UserIsNotPresentException
        user_data = sanitize_dict_for_redis(user)
        await add_user_data_to_redis(user_data)

    return user_data
