from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.user import (
    SendOtpRequest,
    VerifyOtpRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from app.services.auth import AuthService
from app.core.security import get_current_user_id
from app.models.user import UserRole
import uuid

router = APIRouter()


@router.post(
    "/otp/send",
    response_model=SuccessResponse[dict],
    summary="Send OTP to farmer email",
)
async def send_otp(
    payload: SendOtpRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    service = AuthService(db)
    result = await service.send_otp(payload)
    return SuccessResponse(data=result)


@router.post(
    "/otp/verify",
    response_model=SuccessResponse[TokenResponse],
    summary="Verify OTP and receive JWT",
)
async def verify_otp(
    payload: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TokenResponse]:
    service = AuthService(db)
    token_data = await service.verify_otp(payload)
    return SuccessResponse(data=token_data, message="Login successful")


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="Email + password login for officers and admins",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TokenResponse]:
    service = AuthService(db)
    token_data = await service.login_with_password(payload)
    return SuccessResponse(data=token_data, message="Login successful")


@router.get(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="Get current authenticated user profile",
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[UserResponse]:
    service = AuthService(db)
    db_row = await service.get_me(user_id)
    user_resp = UserResponse(
        id=db_row["id"],
        email=db_row["email"],
        full_name=db_row["full_name"],
        phone=db_row.get("phone"),
        role=UserRole(db_row["role"]),
        district=db_row.get("district"),
        state=db_row.get("state", "Uttar Pradesh"),
        is_active=db_row.get("is_active", True),
        preferred_lang=db_row.get("preferred_lang", "en"),
        created_at=db_row["created_at"],
    )
    return SuccessResponse(data=user_resp)


@router.put(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="Update current user profile",
)
async def update_me(
    payload: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[UserResponse]:
    from app.core.config import settings
    import httpx

    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        db_row = await AuthService(db).get_me(user_id)
    else:
        url = f"{settings.supabase_url}/rest/v1/users"
        headers = {
            "apikey": settings.supabase_service_key,
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        resp = httpx.patch(
            url,
            headers=headers,
            params={"id": f"eq.{user_id}"},
            json=update_data,
            timeout=10.0,
        )
        resp.raise_for_status()
        rows = resp.json()
        db_row = rows[0] if rows else await AuthService(db).get_me(user_id)

    user_resp = UserResponse(
        id=db_row["id"],
        email=db_row["email"],
        full_name=db_row["full_name"],
        phone=db_row.get("phone"),
        role=UserRole(db_row["role"]),
        district=db_row.get("district"),
        state=db_row.get("state", "Uttar Pradesh"),
        is_active=db_row.get("is_active", True),
        preferred_lang=db_row.get("preferred_lang", "en"),
        created_at=db_row["created_at"],
    )
    return SuccessResponse(data=user_resp, message="Profile updated")