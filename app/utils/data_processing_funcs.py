from datetime import date
from datetime import datetime

from app.utils.logger_init import logger
from app.users.models import UserRole


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
