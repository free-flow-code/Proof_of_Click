from app.dao.base import BaseDAO
from app.game_items.models import Lots


class LotsDAO(BaseDAO):
    model = Lots
