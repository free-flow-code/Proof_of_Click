from celery import Celery

from app.config import settings

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled"
        ]
)

celery.conf.timezone = "UTC"

celery.conf.beat_schedule = {
    "set-mining-chance": {
        "task": "set_mining_chance",
        "schedule": 3600,
    }
}
