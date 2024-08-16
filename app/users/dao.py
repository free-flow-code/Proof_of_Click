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
