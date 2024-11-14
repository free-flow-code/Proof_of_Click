from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date

from app.game_items.dao import GameItemsDAO
from app.game_items.schemas import SGameItem
from app.users.dependencies import get_current_user
from app.exceptions import AccessDeniedException, ObjectNotFoundException

router = APIRouter(
    prefix="/items",
    tags=["Rare Items"]
)


@router.get("")
async def get_user_items(current_user=Depends(get_current_user)) -> list[SGameItem]:
    """
    Возвращает список игровых предметов пользователя.

    Args:
        current_user: Текущий пользователь.

    Returns:
        list[SGameItem]: Список игровых предметов, принадлежащих текущему пользователю.
    """
    return await GameItemsDAO.find_by_user_id(int(current_user["id"]))


@router.get("/add_item")
async def add_item(
        user_id: int,
        name: str,
        date_at_mine: date,
        redis_key: str,
        image_id: Optional[int] = None,
        current_user=Depends(get_current_user)
):
    """
    Добавляет новый игровой предмет для пользователя. Доступно только для администратора.

    Args:
        user_id (int): Идентификатор пользователя, для которого добавляется предмет.
        name (str): Название предмета.
        date_at_mine (date): Дата добычи предмета.
        redis_key (str): Ключ в Redis, связанный с предметом.
        image_id (Optional[int], optional): Идентификатор изображения предмета. По умолчанию None.
        current_user: Текущий пользователь.

    Returns:
        dict: Содержит сообщение о результате добавления предмета.

    Raises:
        AccessDeniedException: Если текущий пользователь не имеет прав администратора.
    """
    if current_user["role"] != "admin":
        raise AccessDeniedException

    await GameItemsDAO.add(
        user_id=user_id,
        name=name,
        date_at_mine=date_at_mine,
        redis_key=redis_key,
        image_id=image_id
    )
    return {"detail": "Item added successfully"}


@router.delete("/{item_id}")
async def delete_item(item_id: int, current_user=Depends(get_current_user)):
    """
    Удаляет игровой предмет по его идентификатору. Доступно только для администратора.

    Args:
        item_id (int): Идентификатор удаляемого предмета.
        current_user: Текущий пользователь.

    Returns:
        dict: Содержит сообщение о результате удаления предмета.

    Raises:
        AccessDeniedException: Если текущий пользователь не имеет прав администратора.
        ObjectNotFoundException: Если предмет с указанным идентификатором не найден.
    """
    if current_user["role"] != "admin":
        raise AccessDeniedException

    item = await GameItemsDAO.find_one_or_none(id=item_id)
    if not item:
        raise ObjectNotFoundException

    await GameItemsDAO.delete(item_id)
    return {"detail": "Item deleted successfully"}
