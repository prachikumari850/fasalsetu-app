from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.crop import CropStage, CropImage, DiseaseReport, Advisory
from app.models.crop import CropStageName
from app.core.exceptions import NotFoundException
import uuid


class CropStageRepository(BaseRepository):
    model = CropStage

    async def get_by_farm(self, farm_id: uuid.UUID) -> list[CropStage]:
        result = await self.db.execute(
            select(CropStage)
            .where(CropStage.farm_id == farm_id)
            .order_by(CropStage.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_farm_and_stage(
        self, farm_id: uuid.UUID, stage_name: CropStageName
    ) -> CropStage | None:
        result = await self.db.execute(
            select(CropStage).where(
                CropStage.farm_id == farm_id,
                CropStage.stage_name == stage_name,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_stage(
        self,
        farm_id: uuid.UUID,
        stage_name: CropStageName,
        data: dict,
    ) -> CropStage:
        existing = await self.get_by_farm_and_stage(farm_id, stage_name)
        if existing:
            for k, v in data.items():
                if v is not None:
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            stage = CropStage(
                farm_id=farm_id,
                stage_name=stage_name,
                **data,
            )
            self.db.add(stage)
            await self.db.flush()
            await self.db.refresh(stage)
            return stage


class CropImageRepository(BaseRepository):
    model = CropImage

    async def get_by_farm(
        self, farm_id: uuid.UUID, limit: int = 50
    ) -> list[CropImage]:
        result = await self.db.execute(
            select(CropImage)
            .where(CropImage.farm_id == farm_id)
            .order_by(CropImage.captured_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_stage(self, stage_id: uuid.UUID) -> list[CropImage]:
        result = await self.db.execute(
            select(CropImage)
            .where(CropImage.stage_id == stage_id)
            .order_by(CropImage.captured_at.desc())
        )
        return list(result.scalars().all())

    async def check_duplicate_hash(
        self, image_hash: str, farm_id: uuid.UUID
    ) -> bool:
        """Check if this hash exists on a DIFFERENT farm (cross-farm duplicate)."""
        result = await self.db.execute(
            select(func.count())
            .select_from(CropImage)
            .where(
                CropImage.image_hash == image_hash,
                CropImage.farm_id != farm_id,
            )
        )
        count = result.scalar_one()
        return count > 0

    async def count_by_stage(self, stage_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(CropImage)
            .where(CropImage.stage_id == stage_id)
        )
        return result.scalar_one()


class AdvisoryRepository(BaseRepository):
    model = Advisory

    async def get_by_farm(
        self, farm_id: uuid.UUID, unread_only: bool = False
    ) -> list[Advisory]:
        query = select(Advisory).where(Advisory.farm_id == farm_id)
        if unread_only:
            query = query.where(Advisory.is_read == False)
        query = query.order_by(Advisory.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_read(self, advisory_id: uuid.UUID) -> Advisory:
        advisory = await self.get_by_id(advisory_id)
        advisory.is_read = True
        await self.db.flush()
        return advisory