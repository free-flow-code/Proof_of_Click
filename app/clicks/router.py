import logging
from fastapi import APIRouter, Request, Depends
from json import JSONDecodeError

from app.users.dependencies import get_current_user
from app.exceptions import ClicksDataException
from app.redis_init import get_redis

router = APIRouter(
    prefix="/clicks",
    tags=["Clicks"]
)


@router.post("")
async def receive_clicks(request: Request, current_user=Depends(get_current_user), redis=Depends(get_redis)):
    try:
        data = await request.json()
        clicks = data.get("clicks")  # number of clicks (int)
        if clicks is None:
            raise ClicksDataException
    except JSONDecodeError:
        logging.info("JSONDecodeError while receiving clicks")
        return
    #TODO calculate win blocks
    mining_chance = float(await redis.get("mining_chance"))
    await redis.zadd(
        "users_balances",
        {f"{current_user['username']}": round(clicks * current_user["blocks_per_click"] * mining_chance, 3)}
    )
