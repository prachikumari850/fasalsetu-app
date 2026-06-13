from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.crop import CropImageResponse
from app.services.crop import CropService
from app.models.crop import CropStageName
from app.core.security import get_current_user_id
from datetime import datetime, timezone
import uuid

router = APIRouter()


@router.post(
    "/upload",
    response_model=SuccessResponse[CropImageResponse],
    status_code=201,
    summary="Upload a geo-tagged crop image",
)
async def upload_crop_image(
    farm_id: uuid.UUID = Form(...),
    stage_name: CropStageName = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    captured_at: str | None = Form(default=None),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CropImageResponse]:
    captured_dt: datetime | None = None
    if captured_at:
        try:
            captured_dt = datetime.fromisoformat(captured_at).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            captured_dt = None

    image = await CropService(db).upload_crop_image(
        farm_id=farm_id,
        user_id=uuid.UUID(user_id),
        stage_name=stage_name,
        file=file,
        latitude=latitude,
        longitude=longitude,
        captured_at=captured_dt,
    )
    return SuccessResponse(
        data=CropImageResponse.model_validate(image),
        message="Image uploaded successfully",
    )