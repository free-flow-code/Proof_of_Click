from sqlalchemy import select, insert, update, delete, func

from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, offset: int = 0, limit: int = None):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns)
            if limit is not None:
                query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def find_by_model_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(id=model_id)
            result = await session.execute(query)
            return result.mappings().first()

    @classmethod
    async def find_by_user_id(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def find_by_key(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().first()

    @classmethod
    async def count_records_by_key(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(func.count()).select_from(cls.model.__table__).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()  # return model id or null

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model.__table__.columns)
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()

    @classmethod
    async def edit(cls, model_id: int, **data):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == model_id).values(**data).returning(cls.model.__table__.columns)
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()

    @classmethod
    async def delete(cls, user_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).where(cls.model.id == user_id)
            await session.execute(query)
            await session.commit()
