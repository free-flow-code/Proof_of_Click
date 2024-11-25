import os
import asyncio
from celery import shared_task

from app.config import settings
from app.utils.logger_init import celery_poc_logger
from app.utils.boosts_init import init_game_boosts
from app.utils.mining_chance_init import set_mining_chance
from app.game_data.modificators import LAST_MODIFIED_DATA_FILES
from app.utils.users_init import recalculate_users_data_in_redis
from app.utils.game_items_init import init_game_items, set_items_quantity_in_redis


@shared_task(name="set_mining_chance_task")
def set_mining_chance_task():
    """Пересчитать и записать в синглтон новое значение для mining_chance."""
    celery_poc_logger.info("TASK STARTED: set_mining_chance_task")
    loop = asyncio.get_event_loop()
    coroutine = set_mining_chance()
    loop.run_until_complete(coroutine)
    celery_poc_logger.info("TASK FINISHED: set_mining_chance_task")


@shared_task(name="recalculate_users_data_task")
def recalculate_users_data_task():
    """
    Пересчитать и обновить в redis балансы пользователей с автокликером.
    А так же подсчитать выпавшие предметы с кликов автокликера.
    """
    celery_poc_logger.info("TASK STARTED: recalculate_users_data_task")
    loop = asyncio.get_event_loop()
    coroutine = recalculate_users_data_in_redis()
    loop.run_until_complete(coroutine)
    celery_poc_logger.info("TASK FINISHED: recalculate_users_data_task")


@shared_task(name="check_and_update_game_data_files")
def check_and_update_game_data_files():
    """
    Проверяет наличие и время изменения JSON-файлов игровых данных.
    Обновляет данные при необходимости.
    """
    celery_poc_logger.info("TASK STARTED: check_and_update_game_data_files")
    loop = asyncio.get_event_loop()
    for filename in LAST_MODIFIED_DATA_FILES.keys():
        filepath = os.path.join(settings.GAME_DATA_DIR, filename)
        try:
            mtime = os.path.getmtime(filepath)
            if LAST_MODIFIED_DATA_FILES[filename] is None or mtime > LAST_MODIFIED_DATA_FILES[filename]:
                if filename == "boosts.json":
                    init_boosts_coroutine = init_game_boosts()
                    loop.run_until_complete(init_boosts_coroutine)

                    celery_poc_logger.info("boosts.json file updated.")

                elif filename == "game_items.json":
                    init_items_coroutine = init_game_items()
                    loop.run_until_complete(init_items_coroutine)

                    celery_poc_logger.info("game_items.json file updated.")
                    set_items_quantity_coroutine = set_items_quantity_in_redis()
                    loop.run_until_complete(set_items_quantity_coroutine)

                    celery_poc_logger.info("New amount of game items in redis has been installed.")

                LAST_MODIFIED_DATA_FILES[filename] = mtime
        except Exception as err:
            celery_poc_logger.error(f"""An error occurred while checking and updating game data files
            while running the Celery background task: {err}""")
    celery_poc_logger.info("TASK FINISHED: check_and_update_game_data_files")
