import logging
from fastapi import APIRouter, Request, Depends
from json import JSONDecodeError

from app.users.dependencies import get_current_user
from app.exceptions import ClicksDataException
from app.redis_init import get_redis
from app.game_items_init import GameItemsRegistry, get_items_registry
from app.clicks.calculate_funcs import calculate_items_won

router = APIRouter(
    prefix="/clicks",
    tags=["Clicks"]
)


@router.post("")
async def receive_clicks(
        request: Request,
        current_user=Depends(get_current_user),
        redis_client=Depends(get_redis),
        items_registry: GameItemsRegistry = Depends(get_items_registry)
):
    try:
        data = await request.json()
        clicks = data.get("clicks")  # number of clicks (int)
        if clicks is None:
            raise ClicksDataException
    except JSONDecodeError:
        logging.info("JSONDecodeError while receiving clicks")
        return

    mining_chance = float(await redis_client.get("mining_chance"))
    await redis_client.zadd(
        "users_balances",
        {f"{current_user['username']}": round(clicks * float(current_user["blocks_per_click"]) * mining_chance, 3)}
    )

    await calculate_items_won(int(current_user["id"]), items_registry, clicks, redis_client)
