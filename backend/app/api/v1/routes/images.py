from fastapi import APIRouter, Depends, File, Form, UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, AsyncSessionLocal
from app.schemas.common import SuccessResponse
from app.schemas.crop import CropImageResponse
from app.services.crop import CropService
from app.models.crop import CropStageName
from app.core.security import get_current_user_id
from app.ai.pipeline import run_inference_pipeline
from app.core.image_utils import read_image_bytes
from app.core.exceptions import ValidationException
from datetime import datetime, timezone
import uuid
import structlog

logger = structlog.get_logger()
router = APIRouter()


async def _run_ai_in_background(
    image_id: uuid.UUID,
    farm_id: uuid.UUID,
    image_bytes: bytes,
) -> None:
    """
    Background task wrapper — creates its own DB session since the
    request session will be closed by the time this runs.
    """
    async with AsyncSessionLocal() as db:
        try:
            await run_inference_pipeline(
                image_id=image_id,
                farm_id=farm_id,
                image_bytes=image_bytes,
                db=db,
            )
        except Exception as e:
            logger.error(
                "Background AI pipeline error",
                image_id=str(image_id),
                error=str(e),
            )


@router.post(
    "/upload",
    response_model=SuccessResponse[CropImageResponse],
    status_code=201,
    summary="Upload a geo-tagged crop image — AI analysis runs in background",
)
async def upload_crop_image(
    background_tasks: BackgroundTasks,
    farm_id: uuid.UUID          = Form(...),
    stage_name: CropStageName   = Form(...),
    latitude: float             = Form(...),
    longitude: float            = Form(...),
    captured_at: str | None     = Form(default=None),
    file: UploadFile            = File(...),
    user_id: str                = Depends(get_current_user_id),
    db: AsyncSession            = Depends(get_db),
) -> SuccessResponse[CropImageResponse]:

    captured_dt: datetime | None = None
    if captured_at:
        try:
            captured_dt = datetime.fromisoformat(captured_at).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            captured_dt = None

    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValidationException("Unsupported file type. Please upload a JPEG, PNG, or WebP image.")

    # Read image bytes before passing to service
    image_bytes = await read_image_bytes(file)

    # Save to Supabase Storage + database
    image = await CropService(db).upload_crop_image(
        farm_id=farm_id,
        user_id=uuid.UUID(user_id),
        stage_name=stage_name,
        file=file,
        latitude=latitude,
        longitude=longitude,
        captured_at=captured_dt,
        image_bytes_override=image_bytes,
    )

    # Queue AI analysis as background task
    # Returns immediately to the user — analysis happens asynchronously
    background_tasks.add_task(
        _run_ai_in_background,
        image_id=image.id,
        farm_id=farm_id,
        image_bytes=image_bytes,
    )

    logger.info(
        "Image uploaded, AI analysis queued",
        image_id=str(image.id),
        stage=stage_name.value,
    )

    return SuccessResponse(
        data=CropImageResponse.model_validate(image),
        message="Image uploaded successfully. AI analysis is running in background.",
    )
