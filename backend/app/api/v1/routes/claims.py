from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db, AsyncSessionLocal
from app.schemas.common import SuccessResponse
from app.core.security import get_current_user_id
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.claim import Claim, ClaimStatus, DamageType
from app.fraud.engine import run_fraud_engine
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import httpx
import structlog

logger = structlog.get_logger()
router = APIRouter()


class ClaimCreate(BaseModel):
    farm_id:            uuid.UUID
    damage_type:        DamageType
    damage_description: Optional[str]  = None
    estimated_loss:     Optional[float] = None
    affected_acres:     Optional[float] = None


class ClaimDecision(BaseModel):
    status:        ClaimStatus
    officer_notes: Optional[str] = None


# ── Helpers: httpx-based DB access (avoids asyncpg DNS issues on Windows) ────

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


def _fetch_claims_rest(farmer_id: str | None = None) -> list[dict]:
    """Fetch claims from Supabase via REST API."""
    url    = f"{_get_supabase_url()}/rest/v1/claims"
    params = {
        "select": "id,farm_id,farmer_id,status,damage_type,trust_score,submitted_at,created_at",
        "order":  "created_at.desc",
        "limit":  "100",
    }
    if farmer_id:
        params["farmer_id"] = f"eq.{farmer_id}"

    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Claims REST fetch failed", error=str(e))
        return []


def _fetch_claim_rest(claim_id: str) -> dict | None:
    url    = f"{_get_supabase_url()}/rest/v1/claims"
    params = {"id": f"eq.{claim_id}", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Claim REST fetch failed", error=str(e), claim_id=claim_id)
        return None


def _insert_claim_rest(data: dict) -> dict | None:
    url     = f"{_get_supabase_url()}/rest/v1/claims"
    headers = {**_supabase_headers(), "Prefer": "return=representation"}
    try:
        resp = httpx.post(url, headers=headers, json=data, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Claim REST insert failed", error=str(e))
        return None


def _update_claim_rest(claim_id: str, data: dict) -> dict | None:
    url     = f"{_get_supabase_url()}/rest/v1/claims"
    headers = {**_supabase_headers(), "Prefer": "return=representation"}
    params  = {"id": f"eq.{claim_id}"}
    try:
        resp = httpx.patch(url, headers=headers, params=params, json=data, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Claim REST update failed", error=str(e))
        return None


def _fetch_fraud_report_rest(claim_id: str) -> dict | None:
    from app.services.auth import _fetch_user_from_supabase_rest
    url    = f"{_get_supabase_url()}/rest/v1/fraud_reports"
    params = {"claim_id": f"eq.{claim_id}", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Fraud report REST fetch failed", error=str(e))
        return None


def _get_user_role(user_id: str) -> str:
    from app.services.auth import _fetch_user_from_supabase_rest
    row = _fetch_user_from_supabase_rest(user_id)
    return row.get("role", "farmer") if row else "farmer"


async def _run_fraud_background(claim_id: uuid.UUID) -> None:
    async with AsyncSessionLocal() as db:
        try:
            await run_fraud_engine(claim_id=claim_id, db=db)
            await db.commit()
            logger.info("Auto fraud analysis complete", claim_id=str(claim_id))
        except Exception as e:
            logger.error("Auto fraud analysis failed",
                         claim_id=str(claim_id), error=str(e))


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=SuccessResponse[dict],
    status_code=201,
    summary="Submit insurance claim — fraud analysis auto-triggered",
)
async def create_claim(
    payload: ClaimCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:

    claim_data = {
        "farm_id":             str(payload.farm_id),
        "farmer_id":           user_id,
        "status":              ClaimStatus.submitted.value,
        "damage_type":         payload.damage_type.value,
        "damage_description":  payload.damage_description,
        "estimated_loss":      payload.estimated_loss,
        "affected_acres":      payload.affected_acres,
        "submitted_at":        datetime.now(timezone.utc).isoformat(),
    }

    created = _insert_claim_rest(claim_data)
    if not created:
        from app.core.exceptions import FasalSetuException
        raise FasalSetuException(500, "Failed to create claim", "CLAIM_CREATE_FAILED")

    claim_id = uuid.UUID(created["id"])
    background_tasks.add_task(_run_fraud_background, claim_id)

    logger.info(
        "Claim submitted",
        claim_id=str(claim_id),
        farm_id=str(payload.farm_id),
        damage_type=payload.damage_type.value,
    )

    return SuccessResponse(
        data={
            "id":           created["id"],
            "farm_id":      created["farm_id"],
            "farmer_id":    created["farmer_id"],
            "status":       created["status"],
            "damage_type":  created["damage_type"],
            "submitted_at": created.get("submitted_at"),
        },
        message="Claim submitted. Fraud analysis is running.",
    )


@router.get(
    "",
    response_model=SuccessResponse[list[dict]],
    summary="List claims — filtered by role",
)
async def list_claims(
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[list[dict]]:

    role = _get_user_role(user_id)

    if role == "farmer":
        claims = _fetch_claims_rest(farmer_id=user_id)
    else:
        claims = _fetch_claims_rest()

    return SuccessResponse(data=[
        {
            "id":           c["id"],
            "farm_id":      c["farm_id"],
            "status":       c["status"],
            "damage_type":  c["damage_type"],
            "trust_score":  c.get("trust_score"),
            "submitted_at": c.get("submitted_at"),
        }
        for c in claims
    ])


@router.get(
    "/{claim_id}",
    response_model=SuccessResponse[dict],
    summary="Get claim details",
)
async def get_claim(
    claim_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:

    claim = _fetch_claim_rest(str(claim_id))
    if not claim:
        raise NotFoundException("Claim")

    role = _get_user_role(user_id)
    if role == "farmer" and claim["farmer_id"] != user_id:
        raise ForbiddenException("Access denied")

    fraud = _fetch_fraud_report_rest(str(claim_id))

    return SuccessResponse(data={
        "id":                  claim["id"],
        "farm_id":             claim["farm_id"],
        "farmer_id":           claim["farmer_id"],
        "status":              claim["status"],
        "damage_type":         claim["damage_type"],
        "damage_description":  claim.get("damage_description"),
        "estimated_loss":      claim.get("estimated_loss"),
        "affected_acres":      claim.get("affected_acres"),
        "trust_score":         claim.get("trust_score"),
        "submitted_at":        claim.get("submitted_at"),
        "reviewed_at":         claim.get("reviewed_at"),
        "officer_notes":       claim.get("officer_notes"),
        "fraud_analyzed":      fraud is not None,
        "fraud_score":         fraud.get("total_fraud_score") if fraud else None,
        "fraud_flags":         fraud.get("flags", []) if fraud else [],
    })


@router.put(
    "/{claim_id}/decision",
    response_model=SuccessResponse[dict],
    summary="Officer approve / reject / inspect claim",
)
async def claim_decision(
    claim_id: uuid.UUID,
    payload: ClaimDecision,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:

    role = _get_user_role(user_id)
    if role == "farmer":
        raise ForbiddenException("Only officers and admins can make claim decisions")

    claim = _fetch_claim_rest(str(claim_id))
    if not claim:
        raise NotFoundException("Claim")

    valid = {
        ClaimStatus.approved.value,
        ClaimStatus.rejected.value,
        ClaimStatus.needs_inspection.value,
        ClaimStatus.under_review.value,
    }
    if payload.status.value not in valid:
        raise ForbiddenException(f"Invalid decision: {payload.status.value}")

    updated = _update_claim_rest(str(claim_id), {
        "status":        payload.status.value,
        "officer_id":    user_id,
        "officer_notes": payload.officer_notes,
        "reviewed_at":   datetime.now(timezone.utc).isoformat(),
    })

    logger.info(
        "Claim decision recorded",
        claim_id=str(claim_id),
        status=payload.status.value,
        officer_id=user_id,
    )

    return SuccessResponse(
        data={
            "id":          str(claim_id),
            "status":      payload.status.value,
            "reviewed_at": updated.get("reviewed_at") if updated else None,
        },
        message=f"Claim {payload.status.value} successfully.",
    )