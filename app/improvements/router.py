from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date

from app.improvements.dao import ImprovementsDAO
from app.improvements.schemas import SImprovements
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.exceptions import AccessDeniedException, ObjectNotFoundException

router = APIRouter(
    prefix="/boosts",
    tags=["Boosts"]
)


@router.get("")
async def get_user_boosts(user: Users = Depends(get_current_user)) -> list[SImprovements]:
    return await ImprovementsDAO.find_by_user_id(user.id)


@router.get("/add_improvement")
async def add_boost(
        user_id: int,
        name: str,
        purchase_date: date,
        level: int,
        redis_key: str,
        image_id: Optional[int] = None,
        user: Users = Depends(get_current_user)
):
    if user.role.value != "admin":
        raise AccessDeniedException

    await ImprovementsDAO.add(
        user_id=user_id,
        name=name,
        purchase_date=purchase_date,
        level=level,
        redis_key=redis_key,
        image_id=image_id
    )
    return {"detail": "Boost added successfully"}


@router.delete("/boost/{boost_id}")
async def delete_boost(boost_id: int, user: Users = Depends(get_current_user)):
    if user.role.value != "admin":
        raise AccessDeniedException

    item = await ImprovementsDAO.find_one_or_none(id=boost_id)
    if not item:
        raise ObjectNotFoundException

    await ImprovementsDAO.delete(boost_id)
    return {"detail": "Boost deleted successfully"}
