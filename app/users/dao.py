from sqlalchemy import select, desc

from app.database import async_session_maker
from app.dao.base import BaseDAO
from app.users.models import Users


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def get_top_100_users(cls):
        async with async_session_maker() as session:
            query = select(Users.username, Users.blocks_balance).order_by(desc(Users.blocks_balance)).limit(100)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def fetch_users_by_key(cls, offset: int = 0, limit: int = None, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns)

            # Добавляем условие фильтрации для !=
            for column, value in filter_by.items():
                if value is not None:
                    if isinstance(value, tuple):
                        operator, val = value
                        if operator == "!=":
                            query = query.filter(getattr(cls.model, column) != val)
                        else:
                            query = query.filter(getattr(cls.model, column) == val)
                    else:
                        query = query.filter(getattr(cls.model, column) == value)

            # Пагинация
            if limit is not None:
                query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            return result.mappings().all()
