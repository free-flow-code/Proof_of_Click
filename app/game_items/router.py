from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date

from app.game_items.dao import GameItemsDAO
from app.game_items.schemas import SGameItem
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.exceptions import AccessDeniedException, ObjectNotFoundException

router = APIRouter(
    prefix="/items",
    tags=["Rare Items"]
)


@router.get("")
async def get_user_items(user: Users = Depends(get_current_user)) -> list[SGameItem]:
    return await GameItemsDAO.find_by_user_id(user.id)


@router.get("/add_item")
async def add_item(
        user_id: int,
        name: str,
        date_at_mine: date,
        redis_key: str,
        image_id: Optional[int] = None,
        user: Users = Depends(get_current_user)
):
    if user.role.value != "admin":
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
async def delete_item(item_id: int, user: Users = Depends(get_current_user)):
    if user.role.value != "admin":
        raise AccessDeniedException

    item = await GameItemsDAO.find_one_or_none(id=item_id)
    if not item:
        raise ObjectNotFoundException

    await GameItemsDAO.delete(item_id)
    return {"detail": "Item deleted successfully"}
