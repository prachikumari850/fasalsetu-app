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

@router.get(
    "/{farm_id}/analysis/{image_id}",
    response_model=SuccessResponse[dict],
    summary="Get AI analysis results for a specific image",
)
async def get_image_analysis(
    farm_id: uuid.UUID,
    image_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    from app.services.crop import (
        CropService, _fetch_crop_image_rest, _fetch_disease_reports_rest,
    )
    from app.core.exceptions import NotFoundException

    await CropService(db)._verify_farm_access(farm_id, uuid.UUID(user_id))

    image = _fetch_crop_image_rest(str(image_id), str(farm_id))
    if image is None:
        raise NotFoundException("CropImage")

    reports = _fetch_disease_reports_rest(str(image_id))

    return SuccessResponse(data={
        "image_id":        str(image_id),
        "ai_processed":    image.get("ai_processed", False),
        "is_inside_fence": image.get("is_inside_fence", False),
        "reports": [
            {
                "id":           r["id"],
                "disease_name": r["disease_name"],
                "confidence":   float(r["confidence"]),
                "severity":     r["severity"],
                "bbox_data":    r.get("bbox_data"),
                "raw_output":   r.get("raw_output"),
                "detected_at":  r["detected_at"],
            }
            for r in reports
        ],
    })


@router.get(
    "/{farm_id}/health",
    response_model=SuccessResponse[dict],
    summary="Get overall crop health score for a farm",
)
async def get_farm_health(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    from app.services.crop import (
        CropService, _fetch_processed_images_rest, _fetch_disease_reports_for_images_rest,
    )

    await CropService(db)._verify_farm_access(farm_id, uuid.UUID(user_id))

    images = _fetch_processed_images_rest(str(farm_id), limit=20)

    if not images:
        return SuccessResponse(data={
            "farm_id":      str(farm_id),
            "health_score": None,
            "health_class": None,
            "message":      "No analyzed images yet. Upload crop photos to get health score.",
            "total_images": 0,
        })

    image_ids = [img["id"] for img in images]
    reports = _fetch_disease_reports_for_images_rest(image_ids)

    scores = []
    for r in reports:
        raw = r.get("raw_output")
        if raw and "health" in raw:
            scores.append(raw["health"]["health_score"])

    avg_score = int(sum(scores) / len(scores)) if scores else None

    health_class = "unknown"
    if avg_score is not None:
        if avg_score >= 85:
            health_class = "healthy"
        elif avg_score >= 60:
            health_class = "mild_stress"
        elif avg_score >= 35:
            health_class = "moderate_stress"
        else:
            health_class = "severe_stress"

    disease_counts: dict[str, int] = {}
    for r in reports:
        disease_counts[r["disease_name"]] = disease_counts.get(r["disease_name"], 0) + 1

    return SuccessResponse(data={
        "farm_id":          str(farm_id),
        "health_score":     avg_score,
        "health_class":     health_class,
        "total_images":     len(images),
        "analyzed_images":  len(reports),
        "disease_summary":  disease_counts,
        "last_analyzed":    images[0]["captured_at"] if images else None,
    })