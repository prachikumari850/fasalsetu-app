# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from app.database import get_db
# from app.schemas.common import SuccessResponse
# from app.core.security import get_current_user_id
# from app.core.exceptions import ForbiddenException
# from app.repositories.user import UserRepository
# from app.models.user import User, UserRole
# from app.models.farm import Farm
# from app.models.claim import Claim, ClaimStatus
# from app.models.fraud import TrustScore
# import uuid

# router = APIRouter()


# @router.get(
#     "/analytics/overview",
#     response_model=SuccessResponse[dict],
#     summary="Admin dashboard KPIs",
# )
# async def get_overview(
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[dict]:
#     user_repo = UserRepository(db)
#     user      = await user_repo.get_by_id(user_id)
#     if user.role != UserRole.admin:
#         raise ForbiddenException("Admin access required")

#     # Farmer count
#     farmers_r = await db.execute(
#         select(func.count()).select_from(User)
#         .where(User.role == UserRole.farmer)
#     )
#     total_farmers = farmers_r.scalar_one()

#     # Farm count
#     farms_r = await db.execute(
#         select(func.count()).select_from(Farm).where(Farm.is_active == True)
#     )
#     total_farms = farms_r.scalar_one()

#     # Claim counts
#     claims_r = await db.execute(select(func.count()).select_from(Claim))
#     total_claims = claims_r.scalar_one()

#     pending_r = await db.execute(
#         select(func.count()).select_from(Claim)
#         .where(Claim.status == ClaimStatus.submitted)
#     )
#     pending_claims = pending_r.scalar_one()

#     approved_r = await db.execute(
#         select(func.count()).select_from(Claim)
#         .where(Claim.status == ClaimStatus.approved)
#     )
#     approved_claims = approved_r.scalar_one()

#     rejected_r = await db.execute(
#         select(func.count()).select_from(Claim)
#         .where(Claim.status == ClaimStatus.rejected)
#     )
#     rejected_claims = rejected_r.scalar_one()

#     # Average trust score
#     avg_ts_r = await db.execute(
#         select(func.avg(TrustScore.score))
#     )
#     avg_trust = avg_ts_r.scalar_one()

#     return SuccessResponse(data={
#         "total_farmers":    total_farmers,
#         "total_farms":      total_farms,
#         "total_claims":     total_claims,
#         "pending_claims":   pending_claims,
#         "approved_claims":  approved_claims,
#         "rejected_claims":  rejected_claims,
#         "avg_trust_score":  float(avg_trust) if avg_trust else 0.0,
#     })


# @router.get(
#     "/users",
#     response_model=SuccessResponse[list[dict]],
#     summary="List all users — admin only",
# )
# async def list_users(
#     role: str | None = None,
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[list[dict]]:
#     user_repo = UserRepository(db)
#     user      = await user_repo.get_by_id(user_id)
#     if user.role != UserRole.admin:
#         raise ForbiddenException("Admin access required")

#     query = select(User).order_by(User.created_at.desc())
#     if role:
#         try:
#             query = query.where(User.role == UserRole(role))
#         except ValueError:
#             pass

#     result = await db.execute(query)
#     users  = result.scalars().all()

#     return SuccessResponse(data=[
#         {
#             "id":            str(u.id),
#             "email":         u.email,
#             "full_name":     u.full_name,
#             "role":          u.role.value,
#             "district":      u.district,
#             "is_active":     u.is_active,
#             "preferred_lang": u.preferred_lang,
#             "created_at":    u.created_at.isoformat(),
#         }
#         for u in users
#     ])


# @router.put(
#     "/users/{target_user_id}/role",
#     response_model=SuccessResponse[dict],
#     summary="Change a user's role — admin only",
# )
# async def update_user_role(
#     target_user_id: uuid.UUID,
#     payload: dict,
#     user_id: str = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ) -> SuccessResponse[dict]:
#     user_repo = UserRepository(db)
#     user      = await user_repo.get_by_id(user_id)
#     if user.role != UserRole.admin:
#         raise ForbiddenException("Admin access required")

#     target = await user_repo.get_by_id(str(target_user_id))
#     new_role = payload.get("role")
#     try:
#         target.role = UserRole(new_role)
#     except ValueError:
#         from app.core.exceptions import ValidationException
#         raise ValidationException(f"Invalid role: {new_role}")

#     await db.flush()
#     return SuccessResponse(
#         data={"id": str(target.id), "role": target.role.value},
#         message="Role updated successfully",
#     )

from fastapi import APIRouter, Depends
from app.schemas.common import SuccessResponse
from app.core.security import get_current_user_id
from app.core.exceptions import ForbiddenException
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


def _count_rest(table: str, filters: dict | None = None) -> int:
    url     = f"{_get_supabase_url()}/rest/v1/{table}"
    headers = {**_supabase_headers(), "Prefer": "count=exact"}
    params  = {"select": "id", "limit": "1", **(filters or {})}
    try:
        resp = httpx.get(url, headers=headers, params=params, timeout=10.0)
        content_range = resp.headers.get("content-range", "*/0")
        total = int(content_range.split("/")[-1])
        return total
    except Exception as e:
        logger.error("Count REST failed", table=table, error=str(e))
        return 0


def _fetch_avg_trust() -> float:
    url    = f"{_get_supabase_url()}/rest/v1/trust_scores"
    params = {"select": "score", "limit": "1000"}
    try:
        resp  = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        rows  = resp.json()
        if not rows: return 0.0
        return sum(float(r["score"]) for r in rows) / len(rows)
    except Exception:
        return 0.0


@router.get(
    "/analytics/overview",
    response_model=SuccessResponse[dict],
    summary="Admin dashboard KPIs",
)
async def get_overview(
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    role = _get_user_role(user_id)
    if role != "admin":
        raise ForbiddenException("Admin access required")

    total_farmers   = _count_rest("users",  {"role": "eq.farmer"})
    total_farms     = _count_rest("farms",  {"is_active": "eq.true"})
    total_claims    = _count_rest("claims")
    pending_claims  = _count_rest("claims", {"status": "eq.submitted"})
    approved_claims = _count_rest("claims", {"status": "eq.approved"})
    rejected_claims = _count_rest("claims", {"status": "eq.rejected"})
    avg_trust       = _fetch_avg_trust()

    return SuccessResponse(data={
        "total_farmers":    total_farmers,
        "total_farms":      total_farms,
        "total_claims":     total_claims,
        "pending_claims":   pending_claims,
        "approved_claims":  approved_claims,
        "rejected_claims":  rejected_claims,
        "avg_trust_score":  round(avg_trust, 1),
    })


@router.get(
    "/users",
    response_model=SuccessResponse[list[dict]],
    summary="List all users — admin only",
)
async def list_users(
    role: str | None = None,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[list[dict]]:
    caller_role = _get_user_role(user_id)
    if caller_role != "admin":
        raise ForbiddenException("Admin access required")

    url    = f"{_get_supabase_url()}/rest/v1/users"
    params: dict = {
        "select": "id,email,full_name,role,district,is_active,preferred_lang,created_at",
        "order":  "created_at.desc",
        "limit":  "500",
    }
    if role:
        params["role"] = f"eq.{role}"

    try:
        resp  = httpx.get(url, headers=_supabase_headers(), params=params, timeout=10.0)
        resp.raise_for_status()
        users = resp.json()
    except Exception as e:
        logger.error("Users REST fetch failed", error=str(e))
        users = []

    return SuccessResponse(data=users)


@router.put(
    "/users/{target_user_id}/role",
    response_model=SuccessResponse[dict],
    summary="Change a user's role — admin only",
)
async def update_user_role(
    target_user_id: uuid.UUID,
    payload: dict,
    user_id: str = Depends(get_current_user_id),
) -> SuccessResponse[dict]:
    role = _get_user_role(user_id)
    if role != "admin":
        raise ForbiddenException("Admin access required")

    new_role = payload.get("role")
    if new_role not in ("farmer", "officer", "admin"):
        from app.core.exceptions import ValidationException
        raise ValidationException(f"Invalid role: {new_role}")

    url     = f"{_get_supabase_url()}/rest/v1/users"
    headers = {**_supabase_headers(), "Prefer": "return=representation"}
    params  = {"id": f"eq.{str(target_user_id)}"}

    try:
        resp = httpx.patch(
            url, headers=headers, params=params,
            json={"role": new_role}, timeout=10.0,
        )
        resp.raise_for_status()
        rows = resp.json()
    except Exception as e:
        logger.error("Role update failed", error=str(e))
        from app.core.exceptions import FasalSetuException
        raise FasalSetuException(500, "Failed to update role", "UPDATE_FAILED")

    return SuccessResponse(
        data={"id": str(target_user_id), "role": new_role},
        message="Role updated successfully",
    )