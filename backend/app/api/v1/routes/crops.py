from fastapi import APIRouter, Depends, File, Form, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.crop import (
    CropStageCreate, CropStageUpdate, CropStageResponse,
    CropImageResponse, CropTimelineResponse,
)
from app.services.crop import CropService
from app.models.crop import CropStageName
from app.core.security import get_current_user_id
from datetime import datetime, timezone
import uuid

router = APIRouter()


@router.post(
    "/{farm_id}/stages",
    response_model=SuccessResponse[CropStageResponse],
    status_code=201,
    summary="Create or update a crop stage for a farm",
)
async def upsert_crop_stage(
    farm_id: uuid.UUID,
    payload: CropStageCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CropStageResponse]:
    stage = await CropService(db).upsert_stage(
        farm_id=farm_id,
        user_id=uuid.UUID(user_id),
        data=payload,
    )
    return SuccessResponse(
        data=CropStageResponse.model_validate(stage),
        message="Stage saved",
    )


@router.put(
    "/{farm_id}/stages/{stage_id}",
    response_model=SuccessResponse[CropStageResponse],
    summary="Update a specific crop stage",
)
async def update_crop_stage(
    farm_id: uuid.UUID,
    stage_id: uuid.UUID,
    payload: CropStageUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CropStageResponse]:
    stage = await CropService(db).update_stage(
        farm_id=farm_id,
        stage_id=stage_id,
        user_id=uuid.UUID(user_id),
        data=payload,
    )
    return SuccessResponse(data=CropStageResponse.model_validate(stage))


@router.post(
    "/{farm_id}/stages/{stage_id}/complete",
    response_model=SuccessResponse[CropStageResponse],
    summary="Mark a crop stage as complete",
)
async def mark_stage_complete(
    farm_id: uuid.UUID,
    stage_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CropStageResponse]:
    stage = await CropService(db).mark_stage_complete(
        farm_id=farm_id,
        stage_id=stage_id,
        user_id=uuid.UUID(user_id),
    )
    return SuccessResponse(
        data=CropStageResponse.model_validate(stage),
        message="Stage marked as complete",
    )


@router.get(
    "/{farm_id}/timeline",
    response_model=SuccessResponse[CropTimelineResponse],
    summary="Get complete crop timeline for a farm",
)
async def get_timeline(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[CropTimelineResponse]:
    timeline = await CropService(db).get_timeline(
        farm_id=farm_id,
        user_id=uuid.UUID(user_id),
    )
    return SuccessResponse(data=timeline)


@router.get(
    "/{farm_id}/images",
    response_model=SuccessResponse[list[CropImageResponse]],
    summary="Get all uploaded images for a farm",
)
async def get_farm_images(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[CropImageResponse]]:
    images = await CropService(db).get_my_images(
        farm_id=farm_id,
        user_id=uuid.UUID(user_id),
    )
    return SuccessResponse(
        data=[CropImageResponse.model_validate(i) for i in images]
    )