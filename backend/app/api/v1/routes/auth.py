from fastapi import APIRouter, Depends, Request
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
    return SuccessResponse(
        data=token_data,
        message="Login successful",
    )


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
    return SuccessResponse(
        data=token_data,
        message="Login successful",
    )


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
    user = await service.get_me(user_id)
    return SuccessResponse(data=UserResponse.model_validate(user))


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
    from app.repositories.user import UserRepository
    repo = UserRepository(db)
    user = await repo.update(
        uuid.UUID(user_id),
        payload.model_dump(exclude_none=True),
    )
    return SuccessResponse(
        data=UserResponse.model_validate(user),
        message="Profile updated",
    )