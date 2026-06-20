from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.crop import CropImage
from app.models.farm import FarmBoundary
from app.core.geofence import is_point_inside_boundary
import structlog

logger = structlog.get_logger()

# Maximum points this signal contributes
MAX_SCORE = 25.0


async def score_gps_consistency(
    farm_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[float, list[str]]:
    """
    Score GPS consistency of all uploaded images for a farm.

    Rules:
      - 0 images inside fence  → 0 pts
      - 50% images inside      → 12.5 pts
      - 100% images inside     → 25 pts
      - Bonus: all lifecycle stages have at least 1 inside-fence image → full 25

    Returns (score, flags)
    """
    flags: list[str] = []

    # Get all crop images for this farm
    result = await db.execute(
        select(CropImage).where(CropImage.farm_id == farm_id)
    )
    images = result.scalars().all()

    if not images:
        flags.append("NO_IMAGES_UPLOADED")
        return 0.0, flags

    total          = len(images)
    inside_count   = sum(1 for img in images if img.is_inside_fence)
    outside_count  = total - inside_count
    inside_ratio   = inside_count / total

    score = round(MAX_SCORE * inside_ratio, 2)

    if outside_count > 0:
        flags.append(f"GPS_OUTSIDE_FENCE: {outside_count}/{total} images outside boundary")

    if inside_ratio < 0.5:
        flags.append("GPS_MAJORITY_OUTSIDE: More than 50% images outside registered boundary")

    if inside_ratio == 0:
        flags.append("GPS_ALL_OUTSIDE: No images within farm boundary — high fraud risk")

    logger.info(
        "GPS consistency scored",
        farm_id=str(farm_id),
        score=score,
        inside=inside_count,
        total=total,
    )
    return score, flags