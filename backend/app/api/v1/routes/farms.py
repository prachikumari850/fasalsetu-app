from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.farm import FarmCreate, FarmResponse, FarmUpdate
from app.core.security import get_current_user_id
import uuid

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[FarmResponse],
    status_code=201,
    summary="Register a new farm",
)
async def create_farm(
    payload: FarmCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[FarmResponse]:
    from app.services.farm import FarmService
    service = FarmService(db)
    farm = await service.create_farm(user_id=uuid.UUID(user_id), data=payload)
    return SuccessResponse(data=FarmResponse.model_validate(farm), message="Farm registered successfully")


@router.get(
    "/my",
    response_model=SuccessResponse[list[FarmResponse]],
    summary="List all farms for current farmer",
)
async def get_my_farms(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[FarmResponse]]:
    from app.services.farm import FarmService
    service = FarmService(db)
    farms = await service.get_farms_by_owner(uuid.UUID(user_id))
    return SuccessResponse(data=[FarmResponse.model_validate(f) for f in farms])


@router.get(
    "/{farm_id}",
    response_model=SuccessResponse[FarmResponse],
    summary="Get farm details",
)
async def get_farm(
    farm_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[FarmResponse]:
    from app.services.farm import FarmService
    service = FarmService(db)
    farm = await service.get_farm(farm_id=farm_id, requesting_user_id=uuid.UUID(user_id))
    return SuccessResponse(data=FarmResponse.model_validate(farm))