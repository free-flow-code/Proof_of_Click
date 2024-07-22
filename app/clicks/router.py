import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from json import JSONDecodeError

from app.users.models import Users
from app.users.dependencies import get_current_user
from app.exceptions import ClicksDataException
from app.redis import get_redis

router = APIRouter(
    prefix="/clicks",
    tags=["Received clicks"]
)


@router.post("")
async def receive_clicks(request: Request, user: Users = Depends(get_current_user), redis=Depends(get_redis)):
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
    current_clicks = await redis.get(f"{user.id}")
    if current_clicks is None:
        current_clicks = 0.0
    else:
        current_clicks = round(float(current_clicks), 3)
    new_total_clicks = current_clicks + rounded_clicks
    await redis.set(f"{user.id}", new_total_clicks)
