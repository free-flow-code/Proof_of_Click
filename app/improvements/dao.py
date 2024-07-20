from app.dao.base import BaseDAO
from app.improvements.models import Improvements


class ImprovementsDAO(BaseDAO):
    model = Improvements
