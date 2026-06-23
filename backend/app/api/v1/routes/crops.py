# from fastapi import APIRouter, Depends, File, Form, UploadFile, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.database import get_db
# from app.schemas.common import SuccessResponse
# from app.schemas.crop import (
#     CropStageCreate, CropStageUpdate, CropStageResponse,
#     CropImageResponse, CropTimelineResponse,
# )
# from app.services.crop import CropService
# from app.models.crop import CropStageName
# from app.core.security import get_current_user_id
# from datetime import datetime, timezone
# import uuid

# router = APIRouter()


# @router.post(
#     "/{farm_id}/stages",
#     response_model=SuccessResponse[CropStageResponse],
#     status_code=201,
#     summary="Create or update a crop stage for a farm",
# )
# async def upsert_crop_stage(
#     farm_id: uuid.UUID,
#     payload: CropStageCreate,
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[CropStageResponse]:
#     stage = await CropService(db).upsert_stage(
#         farm_id=farm_id,
#         user_id=uuid.UUID(user_id),
#         data=payload,
#     )
#     return SuccessResponse(
#         data=CropStageResponse.model_validate(stage),
#         message="Stage saved",
#     )


# @router.put(
#     "/{farm_id}/stages/{stage_id}",
#     response_model=SuccessResponse[CropStageResponse],
#     summary="Update a specific crop stage",
# )
# async def update_crop_stage(
#     farm_id: uuid.UUID,
#     stage_id: uuid.UUID,
#     payload: CropStageUpdate,
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[CropStageResponse]:
#     stage = await CropService(db).update_stage(
#         farm_id=farm_id,
#         stage_id=stage_id,
#         user_id=uuid.UUID(user_id),
#         data=payload,
#     )
#     return SuccessResponse(data=CropStageResponse.model_validate(stage))


# @router.post(
#     "/{farm_id}/stages/{stage_id}/complete",
#     response_model=SuccessResponse[CropStageResponse],
#     summary="Mark a crop stage as complete",
# )
# async def mark_stage_complete(
#     farm_id: uuid.UUID,
#     stage_id: uuid.UUID,
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[CropStageResponse]:
#     stage = await CropService(db).mark_stage_complete(
#         farm_id=farm_id,
#         stage_id=stage_id,
#         user_id=uuid.UUID(user_id),
#     )
#     return SuccessResponse(
#         data=CropStageResponse.model_validate(stage),
#         message="Stage marked as complete",
#     )


# @router.get(
#     "/{farm_id}/timeline",
#     response_model=SuccessResponse[CropTimelineResponse],
#     summary="Get complete crop timeline for a farm",
# )
# async def get_timeline(
#     farm_id: uuid.UUID,
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[CropTimelineResponse]:
#     timeline = await CropService(db).get_timeline(
#         farm_id=farm_id,
#         user_id=uuid.UUID(user_id),
#     )
#     return SuccessResponse(data=timeline)


# @router.get(
#     "/{farm_id}/images",
#     response_model=SuccessResponse[list[CropImageResponse]],
#     summary="Get all uploaded images for a farm",
# )
# async def get_farm_images(
#     farm_id: uuid.UUID,
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[list[CropImageResponse]]:
#     images = await CropService(db).get_my_images(
#         farm_id=farm_id,
#         user_id=uuid.UUID(user_id),
#     )
#     return SuccessResponse(
#         data=[CropImageResponse.model_validate(i) for i in images]
#     )

"""
crops.py - FastAPI routes for crop lifecycle management.

All DB access uses httpx REST to Supabase PostgREST (HTTPS port 443).
Never uses asyncpg/SQLAlchemy directly — that fails DNS on Windows.
This is the established pattern for this project since Phase 3.
"""
from fastapi import APIRouter, Depends
from app.schemas.common import SuccessResponse
from app.core.security import get_current_user_id
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException
import uuid
import httpx
import structlog

logger = structlog.get_logger()
router = APIRouter()


# ── Supabase REST helpers ─────────────────────────────────────────────────────

def _headers() -> dict:
    from app.core.config import settings
    return {
        "apikey":        settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type":  "application/json",
    }


def _base() -> str:
    from app.core.config import settings
    return settings.supabase_url


def _verify_farm_access_rest(farm_id: str, user_id: str) -> dict:
    """
    Verify the user owns the farm or is an officer/admin.
    Returns the farm row. Raises ForbiddenException if access denied.
    Uses httpx REST — never asyncpg.
    """
    # Fetch farm
    url    = f"{_base()}/rest/v1/farms"
    params = {"id": f"eq.{farm_id}", "limit": "1",
              "select": "id,owner_id,name,is_active"}
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        rows = resp.json()
    except Exception as e:
        logger.error("Farm fetch for access check failed", error=str(e))
        raise NotFoundException("Farm")

    if not rows:
        raise NotFoundException("Farm")

    farm = rows[0]

    # Fetch user role
    from app.services.auth import _fetch_user_from_supabase_rest
    user = _fetch_user_from_supabase_rest(user_id)
    if not user:
        raise ForbiddenException("User not found")

    role = user.get("role", "farmer")

    # Officers and admins can see any farm
    if role in ("officer", "admin"):
        return farm

    # Farmers can only see their own farms
    if farm["owner_id"] != user_id:
        raise ForbiddenException("You do not have access to this farm")

    return farm


def _fetch_stages_rest(farm_id: str) -> list[dict]:
    url    = f"{_base()}/rest/v1/crop_stages"
    params = {
        "farm_id": f"eq.{farm_id}",
        "select":  "id,farm_id,stage_name,expected_date,actual_date,notes,is_completed,created_at",
        "order":   "created_at.asc",
    }
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Stages fetch failed", error=str(e), farm_id=farm_id)
        return []


def _fetch_images_for_stages_batch(stage_ids: list[str]) -> dict[str, list[dict]]:
    """
    Fetch all images for the given stage IDs in ONE REST call.
    Returns dict keyed by stage_id.
    """
    if not stage_ids:
        return {}
    id_list = ",".join(stage_ids)
    url     = f"{_base()}/rest/v1/crop_images"
    params  = {
        "stage_id": f"in.({id_list})",
        "select":   "id,farm_id,stage_id,storage_url,latitude,longitude,"
                    "image_hash,is_inside_fence,ai_processed,captured_at,created_at",
        "order":    "captured_at.asc",
    }
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        rows: list[dict] = resp.json()
    except Exception as e:
        logger.error("Batch image fetch failed", error=str(e))
        return {}

    result: dict[str, list] = {}
    for row in rows:
        sid = row["stage_id"]
        result.setdefault(sid, []).append(row)
    return result


def _fetch_images_for_farm_rest(farm_id: str) -> list[dict]:
    url    = f"{_base()}/rest/v1/crop_images"
    params = {
        "farm_id": f"eq.{farm_id}",
        "select":  "id,farm_id,stage_id,storage_url,latitude,longitude,"
                   "image_hash,is_inside_fence,ai_processed,captured_at,created_at",
        "order":   "captured_at.desc",
        "limit":   "50",
    }
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Farm images fetch failed", error=str(e))
        return []


def _upsert_stage_rest(farm_id: str, stage_name: str, data: dict) -> dict:
    """
    Insert or update a crop stage. Uses Supabase upsert via onConflict.
    """
    url     = f"{_base()}/rest/v1/crop_stages"
    headers = {
        **_headers(),
        "Prefer": "return=representation,resolution=merge-duplicates",
    }
    body = {
        "farm_id":       farm_id,
        "stage_name":    stage_name,
        "expected_date": data.get("expected_date"),
        "notes":         data.get("notes"),
    }

    try:
        resp = httpx.post(
            url,
            headers=headers,
            json=body,
            params={"on_conflict": "farm_id,stage_name"},
            timeout=15.0,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else body
    except Exception as e:
        logger.error("Stage upsert failed", error=str(e))
        raise ValidationException(f"Failed to save stage: {str(e)}")


def _update_stage_rest(stage_id: str, data: dict) -> dict:
    url     = f"{_base()}/rest/v1/crop_stages"
    headers = {**_headers(), "Prefer": "return=representation"}
    params  = {"id": f"eq.{stage_id}"}
    allowed = ["expected_date", "actual_date", "notes", "is_completed"]
    body    = {k: v for k, v in data.items() if k in allowed and v is not None}
    try:
        resp = httpx.patch(url, headers=headers, params=params, json=body, timeout=15.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else {}
    except Exception as e:
        logger.error("Stage update failed", error=str(e))
        raise ValidationException(f"Failed to update stage: {str(e)}")


# ── Stage name ordering ───────────────────────────────────────────────────────

STAGE_ORDER = ["sowing", "germination", "vegetative", "flowering", "pre_harvest"]


def _sort_stages(stages: list[dict]) -> list[dict]:
    order = {s: i for i, s in enumerate(STAGE_ORDER)}
    return sorted(stages, key=lambda s: order.get(s.get("stage_name", ""), 99))


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get(
    "/{farm_id}/timeline",
    response_model=SuccessResponse[dict],
    summary="Get complete 5-stage crop lifecycle timeline with images",
)
async def get_timeline(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    """
    Returns the full crop lifecycle timeline for a farm.
    Two REST calls total:
      1. Fetch all stages for the farm
      2. Batch-fetch all images for those stages
    """
    _verify_farm_access_rest(str(farm_id), user_id)

    stages = _fetch_stages_rest(str(farm_id))

    # Batch fetch all images in one call
    stage_ids   = [s["id"] for s in stages]
    images_map  = _fetch_images_for_stages_batch(stage_ids)

    # Attach images to each stage
    stages_with_images = []
    for stage in _sort_stages(stages):
        stages_with_images.append({
            **stage,
            "images": images_map.get(stage["id"], []),
        })

    # Fill in missing stages so frontend always gets all 5
    existing_names = {s["stage_name"] for s in stages}
    for stage_name in STAGE_ORDER:
        if stage_name not in existing_names:
            stages_with_images.append({
                "id":            None,
                "farm_id":       str(farm_id),
                "stage_name":    stage_name,
                "expected_date": None,
                "actual_date":   None,
                "notes":         None,
                "is_completed":  False,
                "created_at":    None,
                "images":        [],
            })

    # Re-sort after filling gaps
    stages_with_images = sorted(
        stages_with_images,
        key=lambda s: STAGE_ORDER.index(s["stage_name"])
        if s["stage_name"] in STAGE_ORDER else 99,
    )

    return SuccessResponse(data={
        "farm_id":        str(farm_id),
        "stages":         stages_with_images,
        "total_stages":   len(STAGE_ORDER),
        "completed":      sum(1 for s in stages if s.get("is_completed")),
        "has_images":     any(len(imgs) > 0 for imgs in images_map.values()),
    })


@router.post(
    "/{farm_id}/stages",
    response_model=SuccessResponse[dict],
    status_code=201,
    summary="Create or update a crop stage",
)
async def upsert_stage(
    farm_id: uuid.UUID,
    payload: dict,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    _verify_farm_access_rest(str(farm_id), user_id)

    stage_name = payload.get("stage_name")
    if stage_name not in STAGE_ORDER:
        raise ValidationException(
            f"Invalid stage name. Must be one of: {', '.join(STAGE_ORDER)}"
        )

    stage = _upsert_stage_rest(str(farm_id), stage_name, payload)
    return SuccessResponse(data=stage, message="Stage saved successfully")


@router.put(
    "/{farm_id}/stages/{stage_id}",
    response_model=SuccessResponse[dict],
    summary="Update a specific crop stage",
)
async def update_stage(
    farm_id: uuid.UUID,
    stage_id: uuid.UUID,
    payload: dict,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    _verify_farm_access_rest(str(farm_id), user_id)
    stage = _update_stage_rest(str(stage_id), payload)
    return SuccessResponse(data=stage, message="Stage updated successfully")


@router.post(
    "/{farm_id}/stages/{stage_id}/complete",
    response_model=SuccessResponse[dict],
    summary="Mark a crop stage as completed",
)
async def complete_stage(
    farm_id: uuid.UUID,
    stage_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    _verify_farm_access_rest(str(farm_id), user_id)

    from datetime import date
    stage = _update_stage_rest(str(stage_id), {
        "is_completed": True,
        "actual_date":  date.today().isoformat(),
    })
    return SuccessResponse(data=stage, message="Stage marked as completed")


@router.get(
    "/{farm_id}/images",
    response_model=SuccessResponse[list[dict]],
    summary="Get all uploaded images for a farm",
)
async def get_farm_images(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[list[dict]]:
    _verify_farm_access_rest(str(farm_id), user_id)
    images = _fetch_images_for_farm_rest(str(farm_id))
    return SuccessResponse(data=images)


@router.get(
    "/{farm_id}/analysis/{image_id}",
    response_model=SuccessResponse[dict],
    summary="Get AI analysis results for a specific image",
)
async def get_image_analysis(
    farm_id: uuid.UUID,
    image_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    _verify_farm_access_rest(str(farm_id), user_id)

    # Fetch image
    url    = f"{_base()}/rest/v1/crop_images"
    params = {"id": f"eq.{image_id}", "farm_id": f"eq.{farm_id}", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        rows = resp.json()
    except Exception as e:
        raise NotFoundException("CropImage")

    if not rows:
        raise NotFoundException("CropImage")

    image = rows[0]

    # Fetch disease reports for this image
    rpt_url    = f"{_base()}/rest/v1/disease_reports"
    rpt_params = {
        "image_id": f"eq.{image_id}",
        "order":    "detected_at.desc",
    }
    try:
        rpt_resp = httpx.get(
            rpt_url, headers=_headers(), params=rpt_params, timeout=15.0
        )
        rpt_resp.raise_for_status()
        reports = rpt_resp.json()
    except Exception:
        reports = []

    return SuccessResponse(data={
        "image_id":      str(image_id),
        "ai_processed":  image.get("ai_processed", False),
        "is_inside_fence": image.get("is_inside_fence", False),
        "storage_url":   image.get("storage_url"),
        "reports": [
            {
                "id":           r["id"],
                "disease_name": r["disease_name"],
                "confidence":   float(r["confidence"]),
                "severity":     r["severity"],
                "bbox_data":    r.get("bbox_data"),
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
) -> SuccessResponse[dict]:
    _verify_farm_access_rest(str(farm_id), user_id)

    # Get processed images
    images = _fetch_images_for_farm_rest(str(farm_id))
    processed = [img for img in images if img.get("ai_processed")]

    if not processed:
        return SuccessResponse(data={
            "farm_id":      str(farm_id),
            "health_score": None,
            "health_class": None,
            "total_images": len(images),
            "message":      "No analyzed images yet. Upload crop photos to get health score.",
        })

    # Fetch disease reports for processed images
    img_ids = ",".join(img["id"] for img in processed[:20])
    rpt_url = f"{_base()}/rest/v1/disease_reports"
    params  = {"image_id": f"in.({img_ids})", "order": "detected_at.desc"}

    try:
        resp = httpx.get(rpt_url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        reports = resp.json()
    except Exception:
        reports = []

    scores = [
        r["raw_output"]["health"]["health_score"]
        for r in reports
        if r.get("raw_output") and "health" in r["raw_output"]
    ]

    avg_score = int(sum(scores) / len(scores)) if scores else None

    health_class = "unknown"
    if avg_score is not None:
        if avg_score >= 85:   health_class = "healthy"
        elif avg_score >= 60: health_class = "mild_stress"
        elif avg_score >= 35: health_class = "moderate_stress"
        else:                 health_class = "severe_stress"

    disease_counts: dict[str, int] = {}
    for r in reports:
        d = r.get("disease_name", "unknown")
        disease_counts[d] = disease_counts.get(d, 0) + 1

    return SuccessResponse(data={
        "farm_id":          str(farm_id),
        "health_score":     avg_score,
        "health_class":     health_class,
        "total_images":     len(images),
        "analyzed_images":  len(reports),
        "disease_summary":  disease_counts,
    })