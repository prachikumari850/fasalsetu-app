from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.farm import Farm, FarmBoundary
from app.core.exceptions import NotFoundException, ForbiddenException
import uuid


class FarmRepository(BaseRepository):
    model = Farm

    async def get_by_owner(self, owner_id: uuid.UUID) -> list[Farm]:
        result = await self.db.execute(
            select(Farm)
            .where(Farm.owner_id == owner_id, Farm.is_active == True)
            .options(selectinload(Farm.boundary))
            .order_by(Farm.created_at.desc())
        )
        return result.scalars().all()

    async def get_with_boundary(self, farm_id: uuid.UUID) -> Farm:
        result = await self.db.execute(
            select(Farm)
            .where(Farm.id == farm_id)
            .options(selectinload(Farm.boundary))
        )
        farm = result.scalar_one_or_none()
        if farm is None:
            raise NotFoundException("Farm")
        return farm

    async def verify_ownership(
        self, farm_id: uuid.UUID, user_id: uuid.UUID
    ) -> Farm:
        farm = await self.get_with_boundary(farm_id)
        if farm.owner_id != user_id:
            raise ForbiddenException("You do not own this farm")
        return farm

    async def create_with_boundary(
        self, farm: Farm, boundary: FarmBoundary
    ) -> Farm:
        self.db.add(farm)
        await self.db.flush()
        boundary.farm_id = farm.id
        self.db.add(boundary)
        await self.db.flush()
        await self.db.refresh(farm)
        return farm