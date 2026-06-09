from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base import Base
from app.core.exceptions import NotFoundException
import uuid


class BaseRepository:
    model = None

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: uuid.UUID | str):
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            raise NotFoundException(self.model.__tablename__)
        return obj

    async def save(self, obj):
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj):
        await self.db.delete(obj)
        await self.db.flush()