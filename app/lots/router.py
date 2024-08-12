from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date

from app.lots.dao import LotsDAO
from app.lots.schemas import SLots
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.exceptions import AccessDeniedException, ObjectNotFoundException

router = APIRouter(
    prefix="/lots",
    tags=["Lots"]
)


@router.get("")
async def get_user_lots(current_user=Depends(get_current_user)) -> list[SLots]:
    return await LotsDAO.find_by_user_id(int(current_user["id"]))


@router.get("/add_lot")
async def add_lot(
        user_id: int,
        date_at_create: date,
        expiration_date: date,
        game_item_id: int,
        start_price: float,
        best_price: Optional[float],
        best_price_user_id: Optional[int],
        current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise AccessDeniedException

    await LotsDAO.add(
        user_id=user_id,
        date_at_create=date_at_create,
        expiration_date=expiration_date,
        game_item_id=game_item_id,
        start_price=start_price,
        best_price=best_price,
        best_price_user_id=best_price_user_id
    )
    return {"detail": "Lot added successfully"}


@router.delete("/{lot_id}")
async def delete_lot(lot_id: int, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise AccessDeniedException

    item = await LotsDAO.find_one_or_none(id=lot_id)
    if not item:
        raise ObjectNotFoundException

    await LotsDAO.delete(lot_id)
    return {"detail": "Lot deleted successfully"}
