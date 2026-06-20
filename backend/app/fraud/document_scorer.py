from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.farm import Farm
import structlog

logger = structlog.get_logger()

MAX_SCORE = 10.0


async def score_document_validity(
    farm_id: uuid.UUID,
    farmer_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[float, list[str]]:
    """
    Score document completeness and validity.

    Checks:
      - Farm has khasra number registered (+3 pts)
      - Farmer has phone number in profile (+3 pts)
      - Farmer has district set (+2 pts)
      - Farm has area > 0 (+2 pts)

    Returns (score, flags)
    """
    flags: list[str] = []
    score = 0.0

    farm_result = await db.execute(
        select(Farm).where(Farm.id == farm_id)
    )
    farm = farm_result.scalar_one_or_none()

    user_result = await db.execute(
        select(User).where(User.id == farmer_id)
    )
    user = user_result.scalar_one_or_none()

    if farm is None or user is None:
        flags.append("DOCUMENT_ERROR: Farm or farmer record not found")
        return 0.0, flags

    # Khasra number
    if farm.khasra_number:
        score += 3.0
    else:
        flags.append("MISSING_KHASRA: No khasra number registered for farm")

    # Phone number
    if user.phone:
        score += 3.0
    else:
        flags.append("MISSING_PHONE: Farmer phone number not in profile")

    # District
    if user.district or farm.district:
        score += 2.0
    else:
        flags.append("MISSING_DISTRICT: No district information")

    # Area validity
    if farm.area_acres and float(farm.area_acres) > 0:
        score += 2.0
    else:
        flags.append("INVALID_AREA: Farm area is zero or missing")

    logger.info(
        "Document validity scored",
        farm_id=str(farm_id),
        score=score,
    )
    return score, flags 