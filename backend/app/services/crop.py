from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from app.repositories.crop import CropStageRepository, CropImageRepository
from app.repositories.farm import FarmRepository
from app.repositories.user import UserRepository
from app.models.crop import CropStage, CropImage, CropStageName
from app.models.user import UserRole
from app.schemas.crop import (
    CropStageCreate, CropStageUpdate, CropTimelineResponse,
    CropTimelineStage, CropStageResponse, CropImageResponse,
)
from app.core.geofence import is_point_inside_boundary
from app.core.image_utils import (
    read_image_bytes, compute_phash, validate_image
)
from app.core.storage import upload_image_to_storage
from app.core.exceptions import (
    ForbiddenException, ValidationException, NotFoundException
)
from datetime import datetime, timezone
import uuid
import structlog

logger = structlog.get_logger()

# Map stage order for display
STAGE_ORDER = [
    CropStageName.sowing,
    CropStageName.germination,
    CropStageName.vegetative,
    CropStageName.flowering,
    CropStageName.pre_harvest,
]


class CropService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stage_repo = CropStageRepository(db)
        self.image_repo = CropImageRepository(db)
        self.farm_repo = FarmRepository(db)
        self.user_repo = UserRepository(db)

    async def _verify_farm_access(
        self, farm_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        farm = await self.farm_repo.get_with_boundary(farm_id)
        if user.role == UserRole.farmer and farm.owner_id != user_id:
            raise ForbiddenException("You do not own this farm")

    async def upsert_stage(
        self,
        farm_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CropStageCreate,
    ) -> CropStage:
        await self._verify_farm_access(farm_id, user_id)
        return await self.stage_repo.upsert_stage(
            farm_id=farm_id,
            stage_name=data.stage_name,
            data={
                "expected_date": data.expected_date,
                "notes": data.notes,
            },
        )

    async def update_stage(
        self,
        farm_id: uuid.UUID,
        stage_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CropStageUpdate,
    ) -> CropStage:
        await self._verify_farm_access(farm_id, user_id)
        stage = await self.stage_repo.get_by_id(stage_id)
        if stage.farm_id != farm_id:
            raise ForbiddenException("Stage does not belong to this farm")
        update_data = data.model_dump(exclude_none=True)
        for k, v in update_data.items():
            setattr(stage, k, v)
        await self.db.flush()
        await self.db.refresh(stage)
        return stage

    async def upload_crop_image(
        self,
        farm_id: uuid.UUID,
        user_id: uuid.UUID,
        stage_name: CropStageName,
        file: UploadFile,
        latitude: float,
        longitude: float,
        captured_at: datetime | None = None,
        image_bytes_override: bytes | None = None,
) -> CropImage:
     await self._verify_farm_access(farm_id, user_id)

     stage = await self.stage_repo.upsert_stage(
        farm_id=farm_id,
        stage_name=stage_name,
        data={},
    )

    # Use pre-read bytes if provided, otherwise read from file
     image_bytes = image_bytes_override or await read_image_bytes(file)

     error = validate_image(image_bytes)
     if error:
         raise ValidationException(error)

     image_hash = compute_phash(image_bytes)

     farm = await self.farm_repo.get_with_boundary(farm_id)

     is_inside = False
     if farm.boundary and farm.boundary.coordinates:
         coords = farm.boundary.coordinates
         if isinstance(coords, list) and len(coords) >= 3:
             is_inside = is_point_inside_boundary(
                latitude,
                longitude,
                coords,
            )

     filename = file.filename or f"crop_{uuid.uuid4().hex}.jpg"

     storage_path, storage_url = upload_image_to_storage(
         bucket="crop-images",
         user_id=str(user_id),
         image_bytes=image_bytes,
         original_filename=filename,
    )

     crop_image = CropImage(
        farm_id=farm_id,
        stage_id=stage.id,
        uploaded_by=user_id,
        storage_path=storage_path,
        storage_url=storage_url,
        latitude=latitude,
        longitude=longitude,
        image_hash=image_hash,
        is_inside_fence=is_inside,
        ai_processed=False,
        captured_at=captured_at or datetime.now(timezone.utc),
    )

     self.db.add(crop_image)

     await self.db.flush()
     await self.db.refresh(crop_image)

     if not stage.is_completed:
        stage.actual_date = (
            captured_at.date()
            if captured_at
            else datetime.now(timezone.utc).date()
        )
        await self.db.flush()

     return crop_image

    async def get_timeline(
        self,
        farm_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CropTimelineResponse:
        await self._verify_farm_access(farm_id, user_id)

        all_stages = await self.stage_repo.get_by_farm(farm_id)
        stage_map = {s.stage_name: s for s in all_stages}

        timeline_stages: list[CropTimelineStage] = []
        total_images = 0
        completed = 0

        for stage_name in STAGE_ORDER:
            if stage_name in stage_map:
                stage = stage_map[stage_name]
                images = await self.image_repo.get_by_stage(stage.id)
                image_count = len(images)
                total_images += image_count
                if stage.is_completed:
                    completed += 1

                stage_response = CropStageResponse.model_validate(stage)
                stage_response.image_count = image_count

                timeline_stages.append(
                    CropTimelineStage(
                        stage=stage_response,
                        images=[CropImageResponse.model_validate(i) for i in images],
                    )
                )
            else:
                # Stage not yet started — add placeholder
                placeholder = CropStage(
                    id=uuid.uuid4(),
                    farm_id=farm_id,
                    stage_name=stage_name,
                    is_completed=False,
                )
                stage_response = CropStageResponse(
                    id=placeholder.id,
                    farm_id=farm_id,
                    stage_name=stage_name,
                    expected_date=None,
                    actual_date=None,
                    notes=None,
                    is_completed=False,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    image_count=0,
                )
                timeline_stages.append(
                    CropTimelineStage(stage=stage_response, images=[])
                )

        return CropTimelineResponse(
            farm_id=farm_id,
            stages=timeline_stages,
            total_images=total_images,
            completed_stages=completed,
        )

    async def mark_stage_complete(
        self,
        farm_id: uuid.UUID,
        stage_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CropStage:
        await self._verify_farm_access(farm_id, user_id)
        stage = await self.stage_repo.get_by_id(stage_id)
        if stage.farm_id != farm_id:
            raise ForbiddenException("Stage does not belong to this farm")
        stage.is_completed = True
        if not stage.actual_date:
            stage.actual_date = datetime.now(timezone.utc).date()
        await self.db.flush()
        await self.db.refresh(stage)
        return stage

    async def get_my_images(
        self,
        farm_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[CropImage]:
        await self._verify_farm_access(farm_id, user_id)
        return await self.image_repo.get_by_farm(farm_id)
    
