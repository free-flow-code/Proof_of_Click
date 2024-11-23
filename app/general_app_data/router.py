import json
import logging
from pydantic import ValidationError
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.utils.logger_init import logger
from app.users.dependencies import get_current_user
from app.general_app_data.schemas import SBoostsFile
from app.utils.data_processing_funcs import save_json_file
from app.utils.mining_chance_init import get_mining_chance_singleton
from app.exceptions import (
    ValueException,
    IncorrectJsonFileException,
    AccessDeniedException
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


@router.post("/upload-boosts-json")
async def upload_boosts_json(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """
    Загружает и проверяет JSON-файл с данными о бустах.
    """
    if current_user["role"] != "admin":
        raise AccessDeniedException

    if not file.filename.endswith(".json"):
        raise IncorrectJsonFileException
    try:
        content = await file.read()
        data = json.loads(content)
        validated_data = SBoostsFile(**data)

        await save_json_file(validated_data.dict(), "app/game_data/boosts.json")
        return {"status": "success", "data": validated_data.dict()}
    except json.JSONDecodeError:
        logger.error(f"Error reading uploaded json file. File is corrupted or contains invalid data.")
        raise IncorrectJsonFileException
    except ValidationError as err:
        logger.error(f"Validation error of uploaded json file: {err.errors()}")
        raise HTTPException(status_code=422, detail=err.errors())
    except Exception as err:
        logger.error(f"Json file upload error. {err}")
