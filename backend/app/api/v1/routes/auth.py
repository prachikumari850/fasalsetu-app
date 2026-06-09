from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.user import UserResponse, UserCreate
from app.core.security import get_current_user_id
from app.core.logging import logger
import structlog

router = APIRouter()


@router.get(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="Get current authenticated user",
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[UserResponse]:
    from app.repositories.user import UserRepository
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    return SuccessResponse(data=UserResponse.model_validate(user))


@router.put(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="Update current user profile",
)
async def update_me(
    payload: dict,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[UserResponse]:
    from app.repositories.user import UserRepository
    repo = UserRepository(db)
    user = await repo.update(user_id, payload)
    return SuccessResponse(data=UserResponse.model_validate(user), message="Profile updated")