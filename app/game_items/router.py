from fastapi import APIRouter, Depends
from typing import Optional

from app.game_items.dao import GameItemsDAO
from app.game_items.schemas import SGameItem
from app.users.models import Users
from app.users.dependencies import get_current_user

router = APIRouter(
    prefix="/rare_items",
    tags=["Rare Items"]
)


@router.get("")
async def get_user_items(user: Users = Depends(get_current_user)) -> list[SGameItem]:
    return await GameItemsDAO.find_by_user_id(user.id)


@router.get("/{model_id}")
async def get_item_by_id(model_id: int) -> Optional[SGameItem]:
    return await GameItemsDAO.find_by_model_id(model_id)


@router.get("/{user_id}")
async def get_items_by_user_id(user_id: int) -> list[SGameItem]:
    return await GameItemsDAO.find_by_user_id(user_id)
