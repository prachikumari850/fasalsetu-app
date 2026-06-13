from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime, date
import uuid
from app.models.crop import CropStageName, SeverityLevel, AdvisoryPriority


class CropStageCreate(BaseModel):
    stage_name: CropStageName
    expected_date: Optional[date] = None
    notes: Optional[str] = None


class CropStageUpdate(BaseModel):
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None
    actual_date: Optional[date] = None


class CropStageResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    stage_name: CropStageName
    expected_date: Optional[date]
    actual_date: Optional[date]
    notes: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    image_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class CropImageResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    stage_id: Optional[uuid.UUID]
    uploaded_by: uuid.UUID
    storage_url: str
    latitude: float
    longitude: float
    is_inside_fence: bool
    ai_processed: bool
    captured_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DiseaseReportResponse(BaseModel):
    id: uuid.UUID
    image_id: uuid.UUID
    disease_name: str
    confidence: float
    severity: SeverityLevel
    affected_area: Optional[float]
    bbox_data: Optional[Any]
    model_version: str
    detected_at: datetime

    model_config = {"from_attributes": True}


class AdvisoryResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    disease_report_id: Optional[uuid.UUID]
    title_en: str
    title_hi: str
    body_en: str
    body_hi: str
    priority: AdvisoryPriority
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CropTimelineStage(BaseModel):
    stage: CropStageResponse
    images: list[CropImageResponse]

    model_config = {"from_attributes": True}


class CropTimelineResponse(BaseModel):
    farm_id: uuid.UUID
    stages: list[CropTimelineStage]
    total_images: int
    completed_stages: int