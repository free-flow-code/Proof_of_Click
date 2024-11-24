from app.dao.base import BaseDAO
from app.general_app_data.models import MiningChance


class MiningChanceDAO(BaseDAO):
    model = MiningChance
