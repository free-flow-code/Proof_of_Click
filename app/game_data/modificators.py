import os

from app.config import settings
from app.utils.logger_init import logger

LAST_MODIFIED_DATA_FILES = {
    "boosts.json": None,
    "game_items.json": None,
}


def set_modified_date(filenames: list[str] = None) -> None:
    """
    Устанавливает дату последнего изменения для указанных файлов.

    Если список файлов не передан, используются файлы из словаря LAST_MODIFIED_DATA_FILES.

    Args:
        filenames (list[str], optional): Список имен файлов, для которых нужно установить дату последнего изменения.
                                         Если None, обрабатываются все файлы из LAST_MODIFIED_DATA_FILES.

    Returns:
        None
    """
    if filenames is None:
        filenames = LAST_MODIFIED_DATA_FILES.keys()

    try:
        for filename in filenames:
            filepath = os.path.join(settings.GAME_DATA_DIR, filename)
            mtime = os.path.getmtime(filepath)
            LAST_MODIFIED_DATA_FILES[filename] = mtime
    except Exception as err:
        logger.error(f"Error assigning file last update date. {err}")
