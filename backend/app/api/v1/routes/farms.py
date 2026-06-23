"""
farms.py - FastAPI routes for farm management.

KEY PERFORMANCE FIX:
Previously: N farms → N separate httpx SSL connections to fetch boundaries
            Each SSL handshake ~10s on this network
            2 farms × 2 calls = ~40s → Flutter Dio 15s timeout exceeded

Now: N farms → 1 batch httpx call with farm_id=in.(id1,id2,...)
     All boundaries in a single SSL connection = 1-2s total
"""
from fastapi import APIRouter, Depends
from app.schemas.common import SuccessResponse
from app.core.security import get_current_user_id
from app.core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
)
import uuid
import httpx
import structlog

logger = structlog.get_logger()
router = APIRouter()


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


def _get_role(user_id: str) -> str:
    from app.services.auth import _fetch_user_from_supabase_rest
    row = _fetch_user_from_supabase_rest(user_id)
    return row.get("role", "farmer") if row else "farmer"


def _fetch_farms_rest(owner_id: str | None = None) -> list[dict]:
    url = f"{_base()}/rest/v1/farms"
    params: dict = {
        "select":    "id,owner_id,name,village,taluka,district,state,"
                     "area_acres,crop_type,season,khasra_number,is_active,created_at",
        "is_active": "eq.true",
        "order":     "created_at.desc",
        "limit":     "100",
    }
    if owner_id:
        params["owner_id"] = f"eq.{owner_id}"
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Farms REST fetch failed", error=str(e))
        return []


def _fetch_farm_rest(farm_id: str) -> dict | None:
    url = f"{_base()}/rest/v1/farms"
    params = {
        "id":     f"eq.{farm_id}",
        "select": "id,owner_id,name,village,taluka,district,state,"
                  "area_acres,crop_type,season,khasra_number,is_active,created_at",
        "limit":  "1",
    }
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Farm REST fetch failed", error=str(e))
        return None


def _fetch_boundaries_batch(farm_ids: list[str]) -> dict[str, dict]:
    """
    THE KEY FIX: Fetch ALL boundaries in ONE httpx call.
    Uses PostgREST in-filter: farm_id=in.(uuid1,uuid2,uuid3)
    Returns dict keyed by farm_id for O(1) lookup.
    """
    if not farm_ids:
        return {}
    id_list = ",".join(farm_ids)
    url = f"{_base()}/rest/v1/farm_boundaries"
    params = {
        "farm_id": f"in.({id_list})",
        "select":  "farm_id,coordinates,center_lat,center_lng,geojson",
    }
    try:
        resp = httpx.get(url, headers=_headers(), params=params, timeout=15.0)
        resp.raise_for_status()
        return {row["farm_id"]: row for row in resp.json()}
    except Exception as e:
        logger.error("Batch boundary fetch failed", error=str(e),
                     farm_count=len(farm_ids))
        return {}


def _fetch_boundary_single(farm_id: str) -> dict | None:
    result = _fetch_boundaries_batch([farm_id])
    return result.get(farm_id)


def _attach_boundaries(farms: list[dict]) -> list[dict]:
    """
    Attach boundaries to farms using ONE batch REST call.
    2 farms = 2 httpx calls total (1 for farms + 1 for all boundaries).
    Previously = 1 + N calls.
    """
    if not farms:
        return []
    farm_ids     = [f["id"] for f in farms]
    boundary_map = _fetch_boundaries_batch(farm_ids)
    return [{**farm, "boundary": boundary_map.get(farm["id"])} for farm in farms]


def _insert_farm_rest(data: dict) -> dict | None:
    url     = f"{_base()}/rest/v1/farms"
    headers = {**_headers(), "Prefer": "return=representation"}
    try:
        resp = httpx.post(url, headers=headers, json=data, timeout=15.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Farm REST insert failed", error=str(e))
        return None


def _insert_boundary_rest(data: dict) -> dict | None:
    url     = f"{_base()}/rest/v1/farm_boundaries"
    headers = {**_headers(), "Prefer": "return=representation"}
    try:
        resp = httpx.post(url, headers=headers, json=data, timeout=15.0)
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error("Boundary REST insert failed", error=str(e))
        return None


@router.post(
    "",
    response_model=SuccessResponse[dict],
    status_code=201,
    summary="Register a new farm with GPS boundary",
)
async def create_farm(
    payload: dict,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    from app.services.auth import _fetch_user_from_supabase_rest
    user = _fetch_user_from_supabase_rest(user_id)
    if not user:
        raise ForbiddenException("User not found")

    role = user.get("role", "farmer")
    if role not in ("farmer", "admin"):
        raise ForbiddenException("Only farmers can register farms")

    boundary_data = payload.pop("boundary", None)
    if not boundary_data:
        raise ValidationException("Farm boundary is required")

    coords = boundary_data.get("coordinates", [])
    if len(coords) < 3:
        raise ValidationException("Farm boundary needs at least 3 points")

    area = payload.get("area_acres", 0)
    if float(area) <= 0:
        raise ValidationException("Area must be greater than 0")

    farm_data = {
        "owner_id":      user_id,
        "name":          payload.get("name"),
        "village":       payload.get("village"),
        "taluka":        payload.get("taluka"),
        "district":      payload.get("district"),
        "state":         payload.get("state", "Uttar Pradesh"),
        "area_acres":    float(payload.get("area_acres", 0)),
        "crop_type":     payload.get("crop_type"),
        "season":        payload.get("season"),
        "khasra_number": payload.get("khasra_number"),
    }

    created_farm = _insert_farm_rest(farm_data)
    if not created_farm:
        raise ValidationException("Failed to create farm. Please try again.")

    boundary_insert = {
        "farm_id":     created_farm["id"],
        "coordinates": coords,
        "center_lat":  float(boundary_data.get("center_lat", 0)),
        "center_lng":  float(boundary_data.get("center_lng", 0)),
        "geojson":     boundary_data.get("geojson", "{}"),
    }
    created_boundary = _insert_boundary_rest(boundary_insert)

    logger.info("Farm registered", farm_id=created_farm["id"], owner_id=user_id)
    return SuccessResponse(
        data={**created_farm, "boundary": created_boundary},
        message="Farm registered successfully",
    )


@router.get(
    "/my",
    response_model=SuccessResponse[list[dict]],
    summary="List farms for current farmer — 2 REST calls total",
)
async def get_my_farms(
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[list[dict]]:
    farms = _fetch_farms_rest(owner_id=user_id)
    return SuccessResponse(data=_attach_boundaries(farms))


@router.get(
    "",
    response_model=SuccessResponse[list[dict]],
    summary="List all farms (officer/admin)",
)
async def list_all_farms(
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[list[dict]]:
    role = _get_role(user_id)
    if role == "farmer":
        raise ForbiddenException("Access denied")
    farms = _fetch_farms_rest()
    return SuccessResponse(data=_attach_boundaries(farms))


@router.get(
    "/{farm_id}",
    response_model=SuccessResponse[dict],
    summary="Get farm details",
)
async def get_farm(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    farm = _fetch_farm_rest(str(farm_id))
    if not farm:
        raise NotFoundException("Farm")
    role = _get_role(user_id)
    if role == "farmer" and farm["owner_id"] != user_id:
        raise ForbiddenException("Access denied")
    boundary = _fetch_boundary_single(str(farm_id))
    return SuccessResponse(data={**farm, "boundary": boundary})


@router.put(
    "/{farm_id}",
    response_model=SuccessResponse[dict],
    summary="Update farm details",
)
async def update_farm(
    farm_id: uuid.UUID,
    payload: dict,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    farm = _fetch_farm_rest(str(farm_id))
    if not farm:
        raise NotFoundException("Farm")
    if farm["owner_id"] != user_id:
        raise ForbiddenException("You do not own this farm")

    allowed = ["name", "crop_type", "season", "khasra_number"]
    update  = {k: v for k, v in payload.items() if k in allowed and v is not None}
    url     = f"{_base()}/rest/v1/farms"
    headers = {**_headers(), "Prefer": "return=representation"}

    try:
        resp = httpx.patch(
            url, headers=headers,
            params={"id": f"eq.{farm_id}"},
            json=update, timeout=15.0,
        )
        resp.raise_for_status()
        rows    = resp.json()
        updated = rows[0] if rows else farm
    except Exception as e:
        logger.error("Farm update failed", error=str(e))
        raise ValidationException("Failed to update farm")

    boundary = _fetch_boundary_single(str(farm_id))
    return SuccessResponse(
        data={**updated, "boundary": boundary},
        message="Farm updated successfully",
    )


@router.put(
    "/{farm_id}/boundary",
    response_model=SuccessResponse[dict],
    summary="Update farm GPS boundary",
)
async def update_boundary(
    farm_id: uuid.UUID,
    payload: dict,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    farm = _fetch_farm_rest(str(farm_id))
    if not farm:
        raise NotFoundException("Farm")
    if farm["owner_id"] != user_id:
        raise ForbiddenException("You do not own this farm")

    coords = payload.get("coordinates", [])
    if len(coords) < 3:
        raise ValidationException("Boundary needs at least 3 points")

    existing = _fetch_boundary_single(str(farm_id))
    bd = {
        "farm_id":     str(farm_id),
        "coordinates": coords,
        "center_lat":  float(payload.get("center_lat", 0)),
        "center_lng":  float(payload.get("center_lng", 0)),
        "geojson":     payload.get("geojson", "{}"),
    }

    url     = f"{_base()}/rest/v1/farm_boundaries"
    headers = {**_headers(), "Prefer": "return=representation"}

    try:
        if existing:
            resp = httpx.patch(
                url, headers=headers,
                params={"farm_id": f"eq.{farm_id}"},
                json={k: v for k, v in bd.items() if k != "farm_id"},
                timeout=15.0,
            )
        else:
            resp = httpx.post(url, headers=headers, json=bd, timeout=15.0)
        resp.raise_for_status()
        rows    = resp.json()
        updated = rows[0] if rows else bd
    except Exception as e:
        logger.error("Boundary update failed", error=str(e))
        raise ValidationException("Failed to update boundary")

    return SuccessResponse(
        data={**farm, "boundary": updated},
        message="Boundary updated successfully",
    )