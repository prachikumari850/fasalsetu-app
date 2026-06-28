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
import httpx
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


# ── Helpers: httpx-based REST access (avoids asyncpg DNS issues on Windows) ─
# Same proven pattern as claims.py / advisories.py.

def _supabase_headers() -> dict:
    from app.core.config import settings
    return {
        "apikey":        settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type":  "application/json",
    }


def _get_supabase_url() -> str:
    from app.core.config import settings
    return settings.supabase_url


def _fetch_user_role_rest(user_id: str) -> str:
    url = f"{_get_supabase_url()}/rest/v1/users"
    params = {"id": f"eq.{user_id}", "select": "role", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0]["role"] if rows else "farmer"
    except Exception as e:
        logger.error("User role REST fetch failed", error=str(e), user_id=user_id)
        return "farmer"


def _fetch_farm_rest(farm_id: str) -> dict | None:
    url = f"{_get_supabase_url()}/rest/v1/farms"
    params = {"id": f"eq.{farm_id}", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Farm REST fetch failed", error=str(e), farm_id=farm_id)
        return None


def _fetch_crop_stages_rest(farm_id: str) -> list[dict]:
    url = f"{_get_supabase_url()}/rest/v1/crop_stages"
    params = {"farm_id": f"eq.{farm_id}"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Crop stages REST fetch failed", error=str(e), farm_id=farm_id)
        return []


def _fetch_crop_images_rest(stage_id: str) -> list[dict]:
    url = f"{_get_supabase_url()}/rest/v1/crop_images"
    params = {"stage_id": f"eq.{stage_id}"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Crop images REST fetch failed", error=str(e), stage_id=stage_id)
        return []

def _fetch_crop_image_rest(image_id: str, farm_id: str) -> dict | None:
    url = f"{_get_supabase_url()}/rest/v1/crop_images"
    params = {"id": f"eq.{image_id}", "farm_id": f"eq.{farm_id}", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Crop image REST fetch failed", error=str(e), image_id=image_id)
        return None


def _fetch_disease_reports_rest(image_id: str) -> list[dict]:
    url = f"{_get_supabase_url()}/rest/v1/disease_reports"
    params = {"image_id": f"eq.{image_id}", "order": "detected_at.desc"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Disease reports REST fetch failed", error=str(e), image_id=image_id)
        return []


def _fetch_processed_images_rest(farm_id: str, limit: int = 20) -> list[dict]:
    url = f"{_get_supabase_url()}/rest/v1/crop_images"
    params = {
        "farm_id": f"eq.{farm_id}",
        "ai_processed": "eq.true",
        "order": "captured_at.desc",
        "limit": str(limit),
    }
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Processed images REST fetch failed", error=str(e), farm_id=farm_id)
        return []


def _fetch_disease_reports_for_images_rest(image_ids: list[str]) -> list[dict]:
    if not image_ids:
        return []
    url = f"{_get_supabase_url()}/rest/v1/disease_reports"
    ids_filter = ",".join(image_ids)
    params = {
        "image_id": f"in.({ids_filter})",
        "order": "detected_at.desc",
    }
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Disease reports (batch) REST fetch failed", error=str(e))
        return []


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
        """
        REST-based — avoids the asyncpg/getaddrinfo crash on Windows.
        Officers/admins may access any farm; farmers only their own.
        """
        role = _fetch_user_role_rest(str(user_id))
        farm = _fetch_farm_rest(str(farm_id))

        if not farm:
            raise NotFoundException("Farm")

        if role == "farmer" and farm.get("owner_id") != str(user_id):
            raise ForbiddenException("You do not own this farm")

    # ── WRITE-PATH METHODS — unchanged, still SQLAlchemy/asyncpg ──────────
    # Not the cause of the reported 500 (lifecycle page only calls
    # get_timeline). If you see "getaddrinfo failed" when uploading a
    # photo, creating a stage, or marking complete, these need the same
    # REST conversion — flag it and we'll do that as its own task.

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

    # ── get_timeline — REST version, this is what fixes the 500 ───────────

    async def get_timeline(
        self,
        farm_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CropTimelineResponse:
        await self._verify_farm_access(farm_id, user_id)

        all_stages = _fetch_crop_stages_rest(str(farm_id))
        stage_map = {s["stage_name"]: s for s in all_stages}

        timeline_stages: list[CropTimelineStage] = []
        total_images = 0
        completed = 0

        for stage_name in STAGE_ORDER:
            stage_row = stage_map.get(stage_name.value)

            if stage_row:
                images_rows = _fetch_crop_images_rest(stage_row["id"])
                image_count = len(images_rows)
                total_images += image_count
                if stage_row.get("is_completed"):
                    completed += 1

                stage_response = CropStageResponse.model_validate(stage_row)
                stage_response.image_count = image_count

                timeline_stages.append(
                    CropTimelineStage(
                        stage=stage_response,
                        images=[
                            CropImageResponse.model_validate(i)
                            for i in images_rows
                        ],
                    )
                )
            else:
                # Stage not yet started — add placeholder
                placeholder_id = uuid.uuid4()
                stage_response = CropStageResponse(
                    id=placeholder_id,
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