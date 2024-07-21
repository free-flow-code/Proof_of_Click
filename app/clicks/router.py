import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from json import JSONDecodeError

from app.game_items.router import get_user_items
from app.exceptions import ClicksDataException

router = APIRouter(
    prefix="/clicks",
    tags=["Received clicks"]
)


@router.post("")
async def receive_clicks(request: Request):
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
    print(f"Received {rounded_clicks} clicks")

    return JSONResponse(content={"status": "accepted"})
