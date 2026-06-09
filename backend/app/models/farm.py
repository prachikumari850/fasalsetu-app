from sqlalchemy import (
    Column, String, Boolean, Text, Numeric, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
from app.models.base import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False)
    village = Column(String, nullable=False)
    taluka = Column(String, nullable=True)
    district = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, default="Uttar Pradesh")
    area_acres = Column(Numeric(8, 3), nullable=False)
    crop_type = Column(String, nullable=False)
    season = Column(String, nullable=False)
    khasra_number = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="farms")
    boundary = relationship(
        "FarmBoundary", back_populates="farm", uselist=False, lazy="selectin"
    )
    crop_stages = relationship("CropStage", back_populates="farm", lazy="noload")
    claims = relationship("Claim", back_populates="farm", lazy="noload")
    trust_scores = relationship("TrustScore", back_populates="farm", lazy="noload")


class FarmBoundary(Base):
    __tablename__ = "farm_boundaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    coordinates = Column(JSONB, nullable=False)
    center_lat = Column(Numeric(10, 7), nullable=False)
    center_lng = Column(Numeric(10, 7), nullable=False)
    geojson = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    farm = relationship("Farm", back_populates="boundary")