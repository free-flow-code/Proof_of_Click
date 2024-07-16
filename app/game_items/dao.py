from app.dao.base import BaseDAO
from app.game_items.models import GameItems


class GameItemsDAO(BaseDAO):
    model = GameItems
