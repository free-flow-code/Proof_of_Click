import smtplib
from pydantic import EmailStr
from celery import shared_task
from datetime import datetime

from app.config import settings
from app.tasks.celery_init import celery
from app.game_items.dao import GameItemsDAO
from app.tasks.email_templates import (
    create_email_confirmation_template,
    create_restore_password_template
)


@celery.task
def send_verify_code_to_email(verification_code: str, email_to: EmailStr):
    message_content = create_email_confirmation_template(verification_code, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message_content)


@celery.task
def send_restore_password_to_email(username: str, password: str, email_to: EmailStr):
    message_content = create_restore_password_template(username, password, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message_content)


@shared_task
def add_items_to_db(user_id: int, item_key: str, items_count: int, image_id: int):
    """Добавляет выпавшие игровые предметы в базу."""
    for _ in range(items_count):
        GameItemsDAO.add(
            user_id=user_id,
            name=item_key,
            date_at_mine=datetime.utcnow(),
            redis_key=item_key,
            image_id=image_id
        )
