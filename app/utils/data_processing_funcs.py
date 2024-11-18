from datetime import date

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
