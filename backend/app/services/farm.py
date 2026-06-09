from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.farm import FarmRepository
from app.repositories.user import UserRepository
from app.models.farm import Farm, FarmBoundary
from app.schemas.farm import FarmCreate
from app.core.exceptions import ForbiddenException
import uuid
import json


class FarmService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.farm_repo = FarmRepository(db)
        self.user_repo = UserRepository(db)

    async def create_farm(self, user_id: uuid.UUID, data: FarmCreate) -> Farm:
        user = await self.user_repo.get_by_id(user_id)
        if user.role.value not in ("farmer", "admin"):
            raise ForbiddenException("Only farmers can register farms")

        farm = Farm(
            owner_id=user_id,
            name=data.name,
            village=data.village,
            taluka=data.taluka,
            district=data.district,
            state=data.state,
            area_acres=data.area_acres,
            crop_type=data.crop_type,
            season=data.season,
            khasra_number=data.khasra_number,
        )

        boundary = FarmBoundary(
            coordinates=data.boundary.coordinates,
            center_lat=data.boundary.center_lat,
            center_lng=data.boundary.center_lng,
            geojson=data.boundary.geojson,
        )

        return await self.farm_repo.create_with_boundary(farm, boundary)

    async def get_farms_by_owner(self, owner_id: uuid.UUID) -> list[Farm]:
        return await self.farm_repo.get_by_owner(owner_id)

    async def get_farm(
        self, farm_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> Farm:
        user = await self.user_repo.get_by_id(requesting_user_id)
        farm = await self.farm_repo.get_with_boundary(farm_id)
        if user.role.value == "farmer" and farm.owner_id != requesting_user_id:
            raise ForbiddenException("Access denied")
        return farm