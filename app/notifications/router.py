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
    """
    Возвращает список уведомлений пользователя.

    Args:
        current_user: Текущий пользователь.

    Returns:
        list[SNotifications]: Список уведомлений, принадлежащих текущему пользователю.
    """
    return await NotificationsDAO.find_by_user_id(int(current_user["id"]))


@router.get("/add_notification")
async def add_notification(
        user_id: int,
        text: str,
        send_date: date,
        current_user=Depends(get_current_user)
):
    """
    Добавляет новое уведомление для пользователя. Доступно только для администратора.

    Args:
        user_id (int): Идентификатор пользователя, для которого добавляется уведомление.
        text (str): Текст уведомления.
        send_date (date): Дата отправки уведомления.
        current_user: Текущий пользователь.

    Returns:
        dict: Содержит сообщение о результате добавления уведомления.

    Raises:
        AccessDeniedException: Если текущий пользователь не имеет прав администратора.
    """
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
    """
    Удаляет уведомление по его идентификатору. Доступно только для администратора.

    Args:
        notification_id (int): Идентификатор уведомления.
        current_user: Текущий пользователь.

    Returns:
        dict: Содержит сообщение о результате удаления уведомления.

    Raises:
        AccessDeniedException: Если текущий пользователь не имеет прав администратора.
        ObjectNotFoundException: Если уведомление с указанным идентификатором не найдено.
    """
    if current_user["role"] != "admin":
        raise AccessDeniedException

    item = await NotificationsDAO.find_one_or_none(id=notification_id)
    if not item:
        raise ObjectNotFoundException

    await NotificationsDAO.delete(notification_id)
    return {"detail": "Notification deleted successfully"}
