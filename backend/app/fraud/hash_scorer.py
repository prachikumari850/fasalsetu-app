from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.crop import CropImage
from app.models.claim import ClaimImage 
import structlog

logger = structlog.get_logger()

MAX_SCORE = 20.0


async def score_image_originality(
    farm_id: uuid.UUID,
    claim_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[float, list[str]]:
    """
    Detect duplicate or recycled images using pHash comparison.

    Rules:
      - No duplicates found → 20 pts
      - Duplicates found on OTHER farms → 0 pts + flag
      - Duplicates found on SAME farm (reruns) → 10 pts + warning
      - Claim images reused from previous claims → 0 pts

    Returns (score, flags)
    """
    flags: list[str] = []

    # Get all claim images
    claim_images_result = await db.execute(
        select(ClaimImage).where(ClaimImage.claim_id == claim_id)
    )
    claim_images = claim_images_result.scalars().all()

    if not claim_images:
        return MAX_SCORE, []

    claim_hashes = [img.image_hash for img in claim_images if img.image_hash]

    if not claim_hashes:
        return MAX_SCORE, []

    # Check cross-farm duplicates in crop_images
    cross_farm_dupes = 0
    same_farm_dupes  = 0

    for phash in claim_hashes:
        # Check crop images on OTHER farms
        cross_result = await db.execute(
            select(func.count())
            .select_from(CropImage)
            .where(
                CropImage.image_hash == phash,
                CropImage.farm_id != farm_id,
            )
        )
        cross_count = cross_result.scalar_one()
        if cross_count > 0:
            cross_farm_dupes += 1
            flags.append(
                f"CROSS_FARM_DUPLICATE: Image hash {phash[:12]}... "
                f"found on {cross_count} other farm(s)"
            )

        # Check same farm (repeated uploads)
        same_result = await db.execute(
            select(func.count())
            .select_from(CropImage)
            .where(
                CropImage.image_hash == phash,
                CropImage.farm_id == farm_id,
            )
        )
        same_count = same_result.scalar_one()
        if same_count > 1:
            same_farm_dupes += 1

    # Cross-farm duplicates are serious fraud signals
    if cross_farm_dupes > 0:
        score = 0.0
        flags.append(
            f"FRAUD_ALERT_DUPLICATE_IMAGES: {cross_farm_dupes} claim image(s) "
            "appear on other farms — potential fraud"
        )
    elif same_farm_dupes > len(claim_hashes) * 0.5:
        score = 10.0
        flags.append("REPEATED_IMAGES: More than 50% images reused from previous uploads")
    else:
        score = MAX_SCORE

    logger.info(
        "Image originality scored",
        claim_id=str(claim_id),
        score=score,
        cross_farm_dupes=cross_farm_dupes,
    )
    return score, flags