from fastapi import Depends, Request
from jose import jwt, JWTError
from datetime import datetime

from app.config import settings
from app.users.dao import UsersDAO
from app.redis_init import get_redis
from app.utils.data_processing_funcs import sanitize_dict_for_redis
from app.utils.data_processing_funcs import add_user_data_to_redis
from app.exceptions import TokenExpiredException, TokenAbsentException, \
    IncorrectTokenFormatException, UserIsNotPresentException


def get_token(request: Request):
    token = request.cookies.get("poc_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise IncorrectTokenFormatException

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException

    redis_client = await get_redis()
    if await redis_client.exists(f"user_data:{user_id}"):
        user_data = await redis_client.hgetall(f"user_data:{user_id}")
    else:
        user = await UsersDAO.find_by_model_id(int(user_id))
        user_data = sanitize_dict_for_redis(user)
        await add_user_data_to_redis(user_data, redis_client)
        if not user:
            raise UserIsNotPresentException

    return user_data
