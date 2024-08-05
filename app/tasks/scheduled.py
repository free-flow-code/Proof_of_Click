#from aiosmtplib import SMTP
import asyncio
import datetime
from celery import shared_task

from app.config import settings
from app.tasks.celery_init import celery


@shared_task()
async def send_reservation_email(date: datetime.date):
    """Выбрать все бронирования на определенную дату
    и разослать их владельцам напоминания
    tomorrows_bookings = await BookingDAO.get_bookings_for_specific_data(date)
    for booking in tomorrows_bookings:
        message_content = remind_booking_template(booking, booking["user_email"])
        smtp_client = SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True
            )
        async with smtp_client:
            await smtp_client.send_message(message_content)"""
    pass


@celery.task(name="send_tomorrow_reservation_email")
def send_reservation_email_sync():
    """Напомнить о бронировании тем пользователям,
    у кого на завтра запланирован заезд в отель
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    asyncio.run(send_reservation_email(tomorrow))"""
    pass


@celery.task(name="send_three_days_reservation_email")
def send_tomorrow_reservation_email_sync():
    """Напомнить о бронировании тем пользователям,
    у кого через 3 дня запланирован заезд в отель
    today = datetime.date.today()
    after_tree_days = today + datetime.timedelta(days=1)
    asyncio.run(send_reservation_email(after_tree_days))"""
    pass
