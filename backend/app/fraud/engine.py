from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.fraud.gps_scorer       import score_gps_consistency
from app.fraud.lifecycle_scorer import score_lifecycle_completeness
from app.fraud.hash_scorer      import score_image_originality
from app.fraud.weather_scorer   import score_weather_validation
from app.fraud.document_scorer  import score_document_validity
from app.models.claim           import Claim, ClaimStatus
from app.models.fraud           import FraudReport, TrustScore
from app.models.farm            import FarmBoundary

logger = structlog.get_logger()


def _compute_trust_grade(score: float) -> str:
    if score >= 80: return "A"
    if score >= 60: return "B"
    if score >= 40: return "C"
    if score >= 20: return "D"
    return "F"


def _fraud_to_trust(fraud_score: float) -> float:
    """
    Convert a fraud score (higher = more suspicious)
    into a trust score (higher = more trustworthy).
    Trust = 100 - fraud_score, but weighted.
    """
    return round(max(0.0, 100.0 - fraud_score), 2)


async def run_fraud_engine(
    claim_id: uuid.UUID,
    db: AsyncSession,
) -> FraudReport:
    """
    Run the complete fraud detection engine for a claim.

    Signals and weights:
      GPS Consistency      25 pts
      Lifecycle Complete   25 pts
      Image Originality    20 pts
      Weather Validation   20 pts
      Document Validity    10 pts
      ─────────────────────────
      Total               100 pts (trust score)

    Fraud score = 100 - trust score
    """
    logger.info("Fraud engine started", claim_id=str(claim_id))

    # Load claim
    claim_result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = claim_result.scalar_one_or_none()
    if claim is None:
        raise ValueError(f"Claim {claim_id} not found")

    farm_id    = claim.farm_id
    farmer_id  = claim.farmer_id
    damage_type = claim.damage_type

    submitted_date = (
        claim.submitted_at.date()
        if claim.submitted_at
        else datetime.now(timezone.utc).date()
    )

    # Get farm boundary center for weather API
    boundary_result = await db.execute(
        select(FarmBoundary).where(FarmBoundary.farm_id == farm_id)
    )
    boundary = boundary_result.scalar_one_or_none()

    farm_lat = float(boundary.center_lat) if boundary else 20.5937
    farm_lng = float(boundary.center_lng) if boundary else 78.9629

    all_flags: list[str] = []

    # ── Signal 1: GPS Consistency ─────────────────────────────────────────
    gps_score, gps_flags = await score_gps_consistency(farm_id, db)
    all_flags.extend(gps_flags)

    # ── Signal 2: Lifecycle Completeness ─────────────────────────────────
    lifecycle_score, lifecycle_flags = await score_lifecycle_completeness(
        farm_id, submitted_date, db
    )
    all_flags.extend(lifecycle_flags)

    # ── Signal 3: Image Originality ───────────────────────────────────────
    hash_score, hash_flags = await score_image_originality(farm_id, claim_id, db)
    all_flags.extend(hash_flags)

    # ── Signal 4: Weather Validation ─────────────────────────────────────
    weather_score, weather_flags, weather_data = await score_weather_validation(
        lat=farm_lat,
        lng=farm_lng,
        damage_type=damage_type,
        damage_date=submitted_date,
    )
    all_flags.extend(weather_flags)

    # ── Signal 5: Document Validity ───────────────────────────────────────
    doc_score, doc_flags = await score_document_validity(farm_id, farmer_id, db)
    all_flags.extend(doc_flags)

    # ── Composite Scores ─────────────────────────────────────────────────
    total_trust_score = round(
        gps_score + lifecycle_score + hash_score + weather_score + doc_score,
        2,
    )
    total_trust_score = max(0.0, min(100.0, total_trust_score))
    total_fraud_score = round(100.0 - total_trust_score, 2)

    breakdown = {
        "gps":       {"score": gps_score,       "max": 25, "flags": gps_flags},
        "lifecycle": {"score": lifecycle_score,  "max": 25, "flags": lifecycle_flags},
        "hash":      {"score": hash_score,       "max": 20, "flags": hash_flags},
        "weather":   {"score": weather_score,    "max": 20, "flags": weather_flags},
        "document":  {"score": doc_score,        "max": 10, "flags": doc_flags},
    }

    # ── Save FraudReport ─────────────────────────────────────────────────
    # Remove existing report if rerunning
    existing = await db.execute(
        select(FraudReport).where(FraudReport.claim_id == claim_id)
    )
    existing_report = existing.scalar_one_or_none()
    if existing_report:
        await db.delete(existing_report)
        await db.flush()

    fraud_report = FraudReport(
        claim_id=claim_id,
        gps_score=gps_score,
        lifecycle_score=lifecycle_score,
        weather_score=weather_score,
        hash_score=hash_score,
        document_score=doc_score,
        total_fraud_score=total_fraud_score,
        flags=all_flags,
        weather_data=weather_data.get("daily") if weather_data else None,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(fraud_report)

    # ── Update claim trust score ──────────────────────────────────────────
    claim.trust_score = total_trust_score
    await db.flush()

    # ── Save / Update TrustScore for this farm ────────────────────────────
    trust_score_record = TrustScore(
        farm_id=farm_id,
        score=total_trust_score,
        grade=_compute_trust_grade(total_trust_score),
        breakdown=breakdown,
        calculated_at=datetime.now(timezone.utc),
    )
    db.add(trust_score_record)
    await db.flush()
    await db.refresh(fraud_report)

    logger.info(
        "Fraud engine complete",
        claim_id=str(claim_id),
        trust_score=total_trust_score,
        fraud_score=total_fraud_score,
        grade=_compute_trust_grade(total_trust_score),
        flag_count=len(all_flags),
    )

    return fraud_report