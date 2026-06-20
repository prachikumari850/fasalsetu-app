from fastapi import APIRouter, Depends, BackgroundTasks
from app.schemas.common import SuccessResponse
from app.core.security import get_current_user_id
from app.core.exceptions import NotFoundException, ForbiddenException
from app.database import AsyncSessionLocal
from app.fraud.engine import run_fraud_engine
import uuid
import httpx
import structlog

logger = structlog.get_logger()
router = APIRouter()


def _supabase_headers() -> dict:
    from app.core.config import settings
    return {
        "apikey":        settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type":  "application/json",
    }


def _get_supabase_url() -> str:
    from app.core.config import settings
    return settings.supabase_url


def _get_user_role(user_id: str) -> str:
    from app.services.auth import _fetch_user_from_supabase_rest
    row = _fetch_user_from_supabase_rest(user_id)
    return row.get("role", "farmer") if row else "farmer"


def _fetch_fraud_report(claim_id: str) -> dict | None:
    url    = f"{_get_supabase_url()}/rest/v1/fraud_reports"
    params = {"claim_id": f"eq.{claim_id}", "limit": "1"}
    try:
        resp = httpx.get(
            url, headers=_supabase_headers(), params=params, timeout=10.0
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Fraud report REST fetch failed", error=str(e))
        return None


def _fetch_claim(claim_id: str) -> dict | None:
    url    = f"{_get_supabase_url()}/rest/v1/claims"
    params = {"id": f"eq.{claim_id}", "limit": "1"}
    try:
        resp = httpx.get(
            url, headers=_supabase_headers(), params=params, timeout=10.0
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Claim REST fetch failed", error=str(e))
        return None


def _fetch_trust_score(farm_id: str) -> dict | None:
    url    = f"{_get_supabase_url()}/rest/v1/trust_scores"
    params = {
        "farm_id": f"eq.{farm_id}",
        "order":   "calculated_at.desc",
        "limit":   "1",
    }
    try:
        resp = httpx.get(
            url, headers=_supabase_headers(), params=params, timeout=10.0
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Trust score REST fetch failed", error=str(e))
        return None


def _compute_trust_grade(score: float) -> str:
    if score >= 80: return "A"
    if score >= 60: return "B"
    if score >= 40: return "C"
    if score >= 20: return "D"
    return "F"


def _get_recommendation(trust_score: float | None) -> str:
    if trust_score is None: return "pending"
    if trust_score >= 80:   return "approve"
    if trust_score >= 50:   return "needs_inspection"
    return "reject"


async def _run_fraud_background(claim_id: uuid.UUID) -> None:
    async with AsyncSessionLocal() as db:
        try:
            await run_fraud_engine(claim_id=claim_id, db=db)
            await db.commit()
        except Exception as e:
            logger.error(
                "Background fraud engine error",
                claim_id=str(claim_id), error=str(e),
            )


@router.post(
    "/analyze/{claim_id}",
    response_model=SuccessResponse[dict],
    summary="Trigger fraud analysis for a claim — officer/admin only",
)
async def trigger_fraud_analysis(
    claim_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    role = _get_user_role(user_id)
    if role == "farmer":
        raise ForbiddenException("Only officers and admins can trigger fraud analysis")

    claim = _fetch_claim(str(claim_id))
    if not claim:
        raise NotFoundException("Claim")

    background_tasks.add_task(_run_fraud_background, claim_id)
    return SuccessResponse(
        data={"claim_id": str(claim_id), "status": "queued"},
        message="Fraud analysis started.",
    )


@router.get(
    "/trust/{farm_id}",
    response_model=SuccessResponse[dict],
    summary="Get farm trust score",
)
async def get_trust_score(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    ts = _fetch_trust_score(str(farm_id))
    if not ts:
        return SuccessResponse(data={
            "farm_id": str(farm_id),
            "score":   None,
            "grade":   None,
            "message": "No trust score yet. Submit a claim to trigger analysis.",
        })

    score = float(ts["score"])
    return SuccessResponse(data={
        "farm_id":       str(farm_id),
        "score":         score,
        "grade":         ts.get("grade") or _compute_trust_grade(score),
        "breakdown":     ts.get("breakdown"),
        "calculated_at": ts.get("calculated_at"),
    })


@router.get(
    "/{claim_id}",
    response_model=SuccessResponse[dict],
    summary="Get fraud report for a claim",
)
async def get_fraud_report(
    claim_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    role = _get_user_role(user_id)
    if role == "farmer":
        raise ForbiddenException("Fraud reports are only visible to officers and admins")

    report = _fetch_fraud_report(str(claim_id))

    if not report:
        claim = _fetch_claim(str(claim_id))
        if not claim:
            raise NotFoundException("Claim")
        return SuccessResponse(data={
            "claim_id":    str(claim_id),
            "status":      "not_analyzed",
            "message":     "Fraud analysis not yet run.",
            "trust_score": None,
            "fraud_score": None,
            "grade":       None,
            "flags":       [],
            "recommendation": "pending",
        })

    claim       = _fetch_claim(str(claim_id))
    trust_score = float(claim["trust_score"]) if claim and claim.get("trust_score") else None

    return SuccessResponse(data={
        "claim_id":        str(claim_id),
        "status":          "analyzed",
        "trust_score":     trust_score,
        "fraud_score":     float(report["total_fraud_score"]),
        "grade":           _compute_trust_grade(trust_score) if trust_score else None,
        "gps_score":       float(report["gps_score"]),
        "lifecycle_score": float(report["lifecycle_score"]),
        "weather_score":   float(report["weather_score"]),
        "hash_score":      float(report["hash_score"]),
        "document_score":  float(report["document_score"]),
        "flags":           report.get("flags", []),
        "weather_data":    report.get("weather_data"),
        "generated_at":    report.get("generated_at"),
        "recommendation":  _get_recommendation(trust_score),
    })