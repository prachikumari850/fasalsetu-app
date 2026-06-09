from sqlalchemy import (
    Column, String, Boolean, Text, Numeric,
    ForeignKey, Date, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
import enum
from app.models.base import Base


class CropStageName(str, enum.Enum):
    sowing = "sowing"
    germination = "germination"
    vegetative = "vegetative"
    flowering = "flowering"
    pre_harvest = "pre_harvest"


class SeverityLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AdvisoryPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class CropStage(Base):
    __tablename__ = "crop_stages"
    __table_args__ = (UniqueConstraint("farm_id", "stage_name"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage_name = Column(SAEnum(CropStageName), nullable=False)
    expected_date = Column(Date, nullable=True)
    actual_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    farm = relationship("Farm", back_populates="crop_stages")
    images = relationship("CropImage", back_populates="stage", lazy="noload")


class CropImage(Base):
    __tablename__ = "crop_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage_id = Column(
        UUID(as_uuid=True),
        ForeignKey("crop_stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    uploaded_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    storage_path = Column(Text, nullable=False)
    storage_url = Column(Text, nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    image_hash = Column(String, nullable=False, index=True)
    is_inside_fence = Column(Boolean, nullable=False, default=False)
    ai_processed = Column(Boolean, nullable=False, default=False)
    captured_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stage = relationship("CropStage", back_populates="images")
    disease_reports = relationship(
        "DiseaseReport", back_populates="image", lazy="noload"
    )


class DiseaseReport(Base):
    __tablename__ = "disease_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(
        UUID(as_uuid=True),
        ForeignKey("crop_images.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    disease_name = Column(String, nullable=False, index=True)
    confidence = Column(Numeric(5, 4), nullable=False)
    severity = Column(SAEnum(SeverityLevel), nullable=False)
    affected_area = Column(Numeric(5, 2), nullable=True)
    bbox_data = Column(JSONB, nullable=True)
    model_version = Column(String, nullable=False, default="yolov8-v1")
    raw_output = Column(JSONB, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    image = relationship("CropImage", back_populates="disease_reports")
    advisories = relationship("Advisory", back_populates="disease_report", lazy="noload")


class Advisory(Base):
    __tablename__ = "advisories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    disease_report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("disease_reports.id", ondelete="SET NULL"),
        nullable=True,
    )
    title_en = Column(Text, nullable=False)
    title_hi = Column(Text, nullable=False)
    body_en = Column(Text, nullable=False)
    body_hi = Column(Text, nullable=False)
    priority = Column(SAEnum(AdvisoryPriority), nullable=False, default=AdvisoryPriority.medium)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    disease_report = relationship("Advisory", foreign_keys=[disease_report_id], lazy="noload")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title_en = Column(Text, nullable=False)
    title_hi = Column(Text, nullable=False)
    body_en = Column(Text, nullable=False)
    body_hi = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")