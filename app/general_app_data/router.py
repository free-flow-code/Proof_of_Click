import logging
from fastapi import APIRouter, UploadFile, File, Depends

from app.config import settings
from app.redis_init import get_redis
from app.utils.logger_init import logger
from app.users.dependencies import get_current_user
from app.redis_helpers.lua_scripts import total_sum_script
from app.general_app_data.schemas import SBoostsFile, SGameItemsFile
from app.utils.data_processing_funcs import save_json_file, validate_json_file
from app.utils.mining_chance_init import get_mining_chance_singleton
from app.exceptions import (
    ValueException,
    AccessDeniedException,
    InternalServerError
)

router = APIRouter(
    prefix="/general_app_data",
    tags=["General application data"]
)


@router.get("/mining-chance", response_model=float)
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


@router.get("/total-blocks")
async def get_total_blocks_generated(redis_client=Depends(get_redis)) -> float:
    """
    Возвращает количество блоков сгенерированное всеми пользователями за все время.

    Returns:
         float: Количество блоков.
    """
    try:
        script = redis_client.register_script(total_sum_script)
        total_sum = await script(keys=[f"users_balances:{settings.REDIS_NODE_TAG_3}"])
        return total_sum
    except Exception as err:
        logger.error(f"Ошибка получения количества сгенерированных блоков: {err}")
        raise InternalServerError


@router.post("/upload-boosts-json")
async def upload_boosts_json(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """
    Загружает и проверяет JSON-файл с данными о бустах.
    """
    if current_user["role"] != "admin":
        raise AccessDeniedException

    try:
        validated_data = await validate_json_file(file, SBoostsFile)
        await save_json_file(validated_data.dict(), "app/game_data/boosts.json")
        return {"status": "success", "data": validated_data.dict()}
    except Exception as err:
        logger.error(f"Ошибка загрузки файла на сервер: {err}")
        raise InternalServerError


@router.post("/upload-items-json")
async def upload_items_json(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """
    Загружает и проверяет JSON-файл с данными об игровых предметах.
    """
    if current_user["role"] != "admin":
        raise AccessDeniedException

    try:
        validated_data = await validate_json_file(file, SGameItemsFile)
        await save_json_file(validated_data.dict(), "app/game_data/game_items.json")
        return {"status": "success", "data": validated_data.dict()}
    except Exception as err:
        logger.error(f"Ошибка загрузки файла на сервер: {err}")
        raise InternalServerError
