import json
from typing import Optional, Type
from datetime import datetime, date
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, ValidationError

from app.utils.logger_init import logger
from app.users.models import UserRole
from app.config import settings
from app.exceptions import (
    FilepathNotSpecifiedException,
    ObjectNotFoundException,
    IncorrectJsonFileException
)


def sanitize_dict_for_redis(user_data: dict) -> dict:
    """Заменяет НЕ поддерживаемые в redis типы данных, из значений словаря, на поддерживаемые."""
    return {
        k: (
            v.strftime('%Y-%m-%d') if isinstance(v, date) else
            # add "v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else" for last_update_time
            v.value if isinstance(v, UserRole) else
            str(v) if isinstance(v, bool) else
            str(v) if isinstance(v, list) else
            (v if v is not None else '')
        )
        for k, v in user_data.items()
    }


def restore_types_from_redis(user_data: dict) -> dict:
    """Восстанавливает оригинальные типы данных после получения из Redis."""
    return {
        k: (
            None if v == "" else
            True if v == 'True' else
            False if v == 'False' else
            int(v) if isinstance(v, str) and v.isdigit() else
            float(v) if isinstance(v, str) and is_float(v) else
            datetime.strptime(v, '%Y-%m-%d') if isinstance(v, str) and is_date(v) else
            v
        )
        for k, v in user_data.items()
    }


def is_float(value: str) -> bool:
    """Проверяет, можно ли преобразовать строку в float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_date(value: str) -> bool:
    """Проверяет, можно ли преобразовать строку в дату."""
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False


async def get_user_data_tag_in_redis(user_id: int, redis_client) -> Optional[str]:
    """
    Проверяет, какой из тегов Redis содержит данные пользователя.

    Args:
        user_id (int): ID пользователя для поиска данных.
        redis_client: Клиент Redis для выполнения запросов.

    Returns:
        Optional[str]: Тег Redis, содержащий данные пользователя, или None, если данные не найдены.
    """
    for redis_tag in [settings.REDIS_NODE_TAG_1, settings.REDIS_NODE_TAG_2]:
        key = f"user_data:{redis_tag}:{user_id}"
        if await redis_client.exists(key):
            return redis_tag
    return None


def log_execution_time_async(func):
    """
    Декоратор для логирования времени выполнения функции.

    Args:
        func (callable): Функция, время выполнения которой нужно логировать.

    Returns:
        callable: Обёрнутая функция, которая логирует время выполнения.

    Logs:
        - Время выполнения функции в миллисекундах с точностью до 4 знаков после запятой.
    """
    async def wrapper(*args, **kwargs):
        start_time = datetime.now().timestamp()
        result = await func(*args, **kwargs)
        end_time = datetime.now().timestamp()
        execution_time_ms = (end_time - start_time) * 1000
        logger.info(f"Время выполнения функции {func.__name__} - {execution_time_ms:.2f} ms.")
        return result
    return wrapper


def open_json_file(filepath: str = None) -> dict:
    if filepath is None:
        raise FilepathNotSpecifiedException

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            file_data = json.loads(file.read())
            return file_data
    except FileNotFoundError:
        logger.error(f"File {file} not found.")
        raise ObjectNotFoundException
    except json.JSONDecodeError:
        logger.error(f"Error reading json file: {filepath}. File is corrupted or contains invalid data.")
        raise IncorrectJsonFileException
    except Exception as err:
        logger.error(f"Error opening json file. {err}")


async def save_json_file(data: dict, filename: str):
    """
    Асинхронно сохраняет данные в формате JSON в файл.

    Args:
        data (dict): Данные для сохранения.
        filename (str): Имя файла.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error saving JSON to {filename}: {e}")


async def validate_json_file(file: UploadFile, validate_model: Type[BaseModel]):
    if not file.filename.endswith(".json"):
        raise IncorrectJsonFileException

    try:
        content = await file.read()
        data = json.loads(content)
        validated_data = validate_model(**data)
        return validated_data
    except json.JSONDecodeError:
        logger.error(f"Error reading uploaded json file. File is corrupted or contains invalid data.")
        raise IncorrectJsonFileException
    except ValidationError as err:
        logger.error(f"Validation error of uploaded json file: {err.errors()}")
        raise HTTPException(status_code=422, detail=err.errors())
    except Exception as err:
        logger.error(f"Json file upload error. {err}")
