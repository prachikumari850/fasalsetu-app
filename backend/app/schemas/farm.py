from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime
import uuid


class BoundaryCreate(BaseModel):
    coordinates: list[list[float]]
    center_lat: float
    center_lng: float
    geojson: str

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: list) -> list:
        if len(v) < 3:
            raise ValueError("Farm boundary needs at least 3 points")
        for point in v:
            if len(point) != 2:
                raise ValueError("Each coordinate must be [lat, lng]")
        return v


class FarmCreate(BaseModel):
    name: str
    village: str
    taluka: Optional[str] = None
    district: str
    state: str = "Uttar Pradesh"
    area_acres: float
    crop_type: str
    season: str
    khasra_number: Optional[str] = None
    boundary: BoundaryCreate

    @field_validator("area_acres")
    @classmethod
    def validate_area(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Area must be greater than 0")
        return v


class FarmUpdate(BaseModel):
    name: Optional[str] = None
    crop_type: Optional[str] = None
    season: Optional[str] = None


class BoundaryResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    coordinates: Any
    center_lat: float
    center_lng: float
    geojson: str

    model_config = {"from_attributes": True}


class FarmResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    village: str
    taluka: Optional[str]
    district: str
    state: str
    area_acres: float
    crop_type: str
    season: str
    khasra_number: Optional[str]
    is_active: bool
    boundary: Optional[BoundaryResponse]
    created_at: datetime

    model_config = {"from_attributes": True}