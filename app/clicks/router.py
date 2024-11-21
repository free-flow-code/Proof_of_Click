from typing import Optional
from json import JSONDecodeError
from fastapi import APIRouter, Request, Depends

from app.config import settings
from app.redis_init import get_redis
from app.utils.logger_init import logger
from app.utils.rate_limiter import limiter
from app.exceptions import ClicksDataException
from app.users.dependencies import get_current_user
from app.utils.users_init import add_user_data_to_redis
from app.clicks.calculate_funcs import calculate_items_won
from app.utils.mining_chance_init import get_mining_chance_singleton

router = APIRouter(
    prefix="/clicks",
    tags=["Clicks"]
)


@router.post("")
@limiter.limit(f"{int(60/settings.SEND_CLICKS_PERIOD)}/minute")  # Ограничение количества запросов с одного ip
async def receive_clicks(
        request: Request,
        current_user=Depends(get_current_user),
        redis_client=Depends(get_redis)
) -> Optional[dict]:
    """
    Обрабатывает количество кликов, совершённых пользователем, и обновляет баланс,
    а также учитывает выпадение игровых предметов.

    Args:
        request (Request): Объект запроса, содержащий данные о кликах от фронтенда.
        current_user: Текущий пользователь.
        redis_client: Клиент Redis для взаимодействия с базой данных.

    Returns:
        Optional[dict]: Сообщение о возможном выигрыше предметов.

    Raises:
        ClicksDataException: Если данные о кликах не были переданы или они некорректны.

    Notes:
        - В случае успешного получения количества кликов происходит обновление
          баланса пользователя в Redis с учётом вероятности добычи.
        - Также рассчитывается количество выпавших игровых предметов, если они
          были получены, возвращается сообщение о выигрыше предметов.
    """
    # получаем количество кликов с фронтенда (int)
    try:
        data = await request.json()
        clicks = data.get("clicks", None)
        if clicks is None:
            raise ClicksDataException
        elif clicks > settings.SEND_CLICKS_PERIOD * 20:
            # не больше 20 кликов в секунду
            clicks = settings.SEND_CLICKS_PERIOD * 20
    except JSONDecodeError:
        logger.error("JSONDecodeError while receiving clicks")
        return

    singleton = get_mining_chance_singleton()
    mining_chance = singleton.get_value()

    # обновляем баланс пользователя, в зависимости от вероятности добычи блока
    current_user["blocks_balance"] = round(
        float(current_user["blocks_balance"]) + (clicks * float(current_user["blocks_per_click"]) * mining_chance),
        3
    )
    await add_user_data_to_redis(current_user)

    # подсчитываем выпали ли игровые предметы и сколько
    count_won_items = await calculate_items_won(int(current_user["id"]), clicks, redis_client)
    if count_won_items:
        return {"detail": "you won rare items"}
