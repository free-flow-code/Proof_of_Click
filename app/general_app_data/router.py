import logging
from fastapi import APIRouter

from app.utils.mining_chance_init import get_mining_chance_singleton
from app.exceptions import ValueException

router = APIRouter(
    prefix="/general_app_data",
    tags=["General application data"]
)


@router.get("/mining_chance", response_model=float)
async def get_mining_chance() -> float:
    """
    Получить текущее значение шанса добычи.

    Возвращает значение шанса добычи, которое хранится в синглтоне.
    Если значение не установлено, возвращает ошибку и записывает ее в лог.

    Returns:
        float: Значение шанса добычи.

    Raises:
        ValueError: Если значение шанса добычи не установлено.
    """
    singleton = get_mining_chance_singleton()
    try:
        mining_chance = singleton.get_value()
        return mining_chance
    except ValueError as err:
        logging.error(f"Ошибка получения шанса добычи: {err}")
        raise ValueException
