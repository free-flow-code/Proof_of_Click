import logging
from fastapi import APIRouter, Request, Depends
from json import JSONDecodeError
from redis.exceptions import ConnectionError

from app.users.models import Users
from app.users.dependencies import get_current_user
from app.exceptions import ClicksDataException
from app.redis_init import get_redis
from app.exceptions import InternalServerError

router = APIRouter(
    prefix="/clicks",
    tags=["Clicks"]
)


@router.get("/get_data")
async def get_clicks_data(current_user: Users = Depends(get_current_user)):
    user = dict(current_user)
    keys_to_send = [
        "username",
        "mail",
        "blocks_balance",
        "clicks_per_sec",
        "blocks_per_click"
    ]
    return {key: user[key] for key in keys_to_send if key in user}


@router.post("")
async def receive_clicks(request: Request, current_user: Users = Depends(get_current_user), redis=Depends(get_redis)):
    try:
        data = await request.json()
        clicks = data.get("clicks")
        rounded_clicks = round(clicks, 3)
        if clicks is None:
            raise ClicksDataException
    except JSONDecodeError:
        logging.info("JSONDecodeError while receiving clicks")
        return

    # Обработка кликов
    try:
        current_clicks = await redis.get(f"{current_user.id}_clicks")
        if current_clicks is None:
            current_clicks = 0.0
        else:
            current_clicks = round(float(current_clicks), 3)
        new_total_clicks = current_clicks + rounded_clicks
        await redis.set(f"{current_user.id}_clicks", new_total_clicks)
    except ConnectionError as err:
        logging.info(f"Redis connection error. {err}")
        raise InternalServerError
