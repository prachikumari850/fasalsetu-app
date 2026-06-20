from __future__ import annotations
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.crop import CropStage, CropImage, CropStageName
import structlog

logger = structlog.get_logger()

MAX_SCORE = 25.0

# Ordered stages — all must be present for full score
REQUIRED_STAGES = [
    CropStageName.sowing,
    CropStageName.germination,
    CropStageName.vegetative,
    CropStageName.flowering,
    CropStageName.pre_harvest,
]


async def score_lifecycle_completeness(
    farm_id: uuid.UUID,
    claim_submitted_at: date,
    db: AsyncSession,
) -> tuple[float, list[str]]:
    """
    Score lifecycle completeness before the claim date.

    Rules:
      - Each stage with at least 1 image uploaded BEFORE claim date = 5 pts
      - 5 stages × 5 pts = 25 pts maximum
      - Images uploaded AFTER claim date do not count

    Returns (score, flags)
    """
    flags: list[str] = []

    # Get all stages for this farm
    stages_result = await db.execute(
        select(CropStage).where(CropStage.farm_id == farm_id)
    )
    stages = {s.stage_name: s for s in stages_result.scalars().all()}

    # Get all images uploaded before the claim date
    images_result = await db.execute(
        select(CropImage).where(CropImage.farm_id == farm_id)
    )
    all_images = images_result.scalars().all()

    # Filter images uploaded before claim
    pre_claim_images = [
        img for img in all_images
        if img.captured_at.date() <= claim_submitted_at
    ]

    # Group images by stage
    stage_image_map: dict[uuid.UUID, list] = {}
    for img in pre_claim_images:
        if img.stage_id:
            stage_image_map.setdefault(img.stage_id, []).append(img)

    completed_stages = 0
    pts_per_stage    = MAX_SCORE / len(REQUIRED_STAGES)

    for stage_name in REQUIRED_STAGES:
        stage = stages.get(stage_name)
        if stage is None:
            flags.append(f"MISSING_STAGE: {stage_name.value} not recorded")
            continue

        stage_images = stage_image_map.get(stage.id, [])
        if not stage_images:
            flags.append(
                f"NO_IMAGES_FOR_STAGE: {stage_name.value} has no images before claim date"
            )
            continue

        completed_stages += 1

    score = round(pts_per_stage * completed_stages, 2)

    if completed_stages < 3:
        flags.append(
            f"INCOMPLETE_LIFECYCLE: Only {completed_stages}/5 stages documented — "
            "minimum 3 required for full verification"
        )

    # Check for suspicious image uploads (all images uploaded same day)
    if len(pre_claim_images) > 3:
        upload_dates = {img.captured_at.date() for img in pre_claim_images}
        if len(upload_dates) == 1:
            flags.append(
                "BULK_SAME_DAY_UPLOAD: All images uploaded on the same date — "
                "suspicious lifecycle documentation"
            )

    logger.info(
        "Lifecycle scored",
        farm_id=str(farm_id),
        score=score,
        completed_stages=completed_stages,
    )
    return score, flags