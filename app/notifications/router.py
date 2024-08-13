from fastapi import APIRouter, Depends
from datetime import date

from app.notifications.dao import NotificationsDAO
from app.notifications.schemas import SNotifications
from app.users.dependencies import get_current_user
from app.exceptions import AccessDeniedException, ObjectNotFoundException

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("")
async def get_user_notifications(current_user=Depends(get_current_user)) -> list[SNotifications]:
    return await NotificationsDAO.find_by_user_id(int(current_user["id"]))


@router.get("/add_notification")
async def add_notification(
        user_id: int,
        text: str,
        send_date: date,
        current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise AccessDeniedException

    await NotificationsDAO.add(
        user_id=user_id,
        text=text,
        send_date=send_date
    )
    return {"detail": "Notification added successfully"}


@router.delete("/{notification_id}")
async def delete_notification(notification_id: int, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise AccessDeniedException

    item = await NotificationsDAO.find_one_or_none(id=notification_id)
    if not item:
        raise ObjectNotFoundException

    await NotificationsDAO.delete(notification_id)
    return {"detail": "Notification deleted successfully"}
