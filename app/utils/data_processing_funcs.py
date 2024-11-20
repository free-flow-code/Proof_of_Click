from typing import Optional
from datetime import datetime, date

from app.utils.logger_init import logger
from app.users.models import UserRole
from app.config import settings


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
