from pydantic import EmailStr
import smtplib

from app.config import settings
from app.tasks.celery_init import celery
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
