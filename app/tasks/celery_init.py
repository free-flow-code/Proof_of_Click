from celery import Celery
from celery.schedules import timedelta

from app.config import settings

celery = Celery(
    "tasks",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//",
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled"
        ]
)

celery.conf.timezone = "UTC"

celery.conf.beat_schedule = {
    "set-mining-chance": {
        "task": "set_mining_chance_task",
        "schedule": timedelta(hours=1),
    },
    "check_and_update_game_data_files": {
        "task": "check_and_update_game_data_files",
        "schedule": timedelta(hours=1),
    },
    "recalculate_users_data": {
        "task": "recalculate_users_data_task",
        "schedule": timedelta(seconds=5)
    }
}
