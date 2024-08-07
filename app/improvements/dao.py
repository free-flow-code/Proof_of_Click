from sqlalchemy import select

from app.database import async_session_maker
from app.dao.base import BaseDAO
from app.improvements.models import Improvements


class ImprovementsDAO(BaseDAO):
    model = Improvements

    @classmethod
    async def get_user_boost_by_name(cls, user_id: int, boost_name: str):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).where(
                cls.model.user_id == user_id,
                cls.model.name == boost_name
            )
            result = await session.execute(query)
            return result.mappings().first()
