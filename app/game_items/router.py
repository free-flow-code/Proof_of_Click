from fastapi import APIRouter

from app.game_items.dao import GameItemsDAO

router = APIRouter(
    prefix="/rare_items",
    tags=["Rare Items"]
)


@router.get("")
async def get_all_items():
    return await GameItemsDAO.find_all()


@router.get("/{item_id}")
async def get_item_by_id(item_id: int):
    pass


@router.get("/user/{user_id}")
async def get_user_items(user_id: int):
    pass
