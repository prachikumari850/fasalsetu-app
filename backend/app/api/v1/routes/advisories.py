from fastapi import APIRouter, Depends
from app.schemas.common import SuccessResponse
from app.schemas.crop import AdvisoryResponse
from app.core.security import get_current_user_id
from app.core.exceptions import NotFoundException, ForbiddenException
import uuid
import httpx
import structlog

logger = structlog.get_logger()
router = APIRouter()


# ── Helpers: httpx-based REST access (avoids asyncpg DNS issues on Windows) ─
# Mirrors the exact pattern already used successfully in claims.py and
# fraud.py — direct asyncpg/SQLAlchemy connections fail with
# "getaddrinfo failed" on this machine, so every route in this app talks
# to Supabase via its REST API instead of a direct Postgres connection.

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


def _fetch_farm_rest(farm_id: str) -> dict | None:
    url    = f"{_get_supabase_url()}/rest/v1/farms"
    params = {"id": f"eq.{farm_id}", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Farm REST fetch failed", error=str(e), farm_id=farm_id)
        return None


def _fetch_advisories_rest(
    farm_id: str,
    unread_only: bool = False,
) -> list[dict]:
    url    = f"{_get_supabase_url()}/rest/v1/advisories"
    params = {
        "select":  "id,farm_id,disease_report_id,title_en,title_hi,body_en,body_hi,priority,is_read,created_at",
        "farm_id": f"eq.{farm_id}",
        "order":   "created_at.desc",
        "limit":   "100",
    }
    if unread_only:
        params["is_read"] = "eq.false"

    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Advisories REST fetch failed", error=str(e), farm_id=farm_id)
        return []


def _fetch_advisory_rest(advisory_id: str) -> dict | None:
    url    = f"{_get_supabase_url()}/rest/v1/advisories"
    params = {"id": f"eq.{advisory_id}", "limit": "1"}
    try:
        resp = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Advisory REST fetch failed", error=str(e), advisory_id=advisory_id)
        return None


def _update_advisory_rest(advisory_id: str, data: dict) -> dict | None:
    url     = f"{_get_supabase_url()}/rest/v1/advisories"
    headers = {**_supabase_headers(), "Prefer": "return=representation"}
    params  = {"id": f"eq.{advisory_id}"}
    try:
        resp = httpx.patch(url, headers=headers, params=params, json=data, timeout=10.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Advisory REST update failed", error=str(e), advisory_id=advisory_id)
        return None


def _get_user_role(user_id: str) -> str:
    from app.services.auth import _fetch_user_from_supabase_rest
    row = _fetch_user_from_supabase_rest(user_id)
    return row.get("role", "farmer") if row else "farmer"


def _verify_farm_ownership(farm_id: str, user_id: str) -> dict:
    """
    Officers/admins can view any farm's advisories.
    Farmers can only view advisories for farms they own.
    Raises NotFoundException / ForbiddenException, otherwise returns the farm row.
    """
    farm = _fetch_farm_rest(farm_id)
    if not farm:
        raise NotFoundException("Farm")

    role = _get_user_role(user_id)
    if role == "farmer" and farm.get("owner_id") != user_id:
        raise ForbiddenException("You do not have access to this farm")

    return farm


# ── Routes ────────────────────────────────────────────────────────────────

@router.get(
    "/{farm_id}",
    response_model=SuccessResponse[list[AdvisoryResponse]],
    summary="Get advisories for a farm",
)
async def get_farm_advisories(
    farm_id: uuid.UUID,
    unread_only: bool = False,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[list[AdvisoryResponse]]:
    _verify_farm_ownership(str(farm_id), user_id)

    rows = _fetch_advisories_rest(str(farm_id), unread_only=unread_only)
    return SuccessResponse(
        data=[AdvisoryResponse.model_validate(row) for row in rows]
    )


@router.put(
    "/{advisory_id}/read",
    response_model=SuccessResponse[AdvisoryResponse],
    summary="Mark an advisory as read",
)
async def mark_advisory_read(
    advisory_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[AdvisoryResponse]:
    existing = _fetch_advisory_rest(str(advisory_id))
    if not existing:
        raise NotFoundException("Advisory")

    # Confirm the requesting user actually owns the farm this advisory belongs to.
    _verify_farm_ownership(existing["farm_id"], user_id)

    updated = _update_advisory_rest(str(advisory_id), {"is_read": True})
    if not updated:
        raise NotFoundException("Advisory")

    return SuccessResponse(data=AdvisoryResponse.model_validate(updated))