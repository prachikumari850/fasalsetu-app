from sqlalchemy import (
    Column, String, Numeric, Text, ForeignKey,
    Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
import enum
from app.models.base import Base


class ClaimStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    needs_inspection = "needs_inspection"


class DamageType(str, enum.Enum):
    drought = "drought"
    flood = "flood"
    hail = "hail"
    pest = "pest"
    disease = "disease"
    fire = "fire"
    other = "other"


class Claim(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    farmer_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    status = Column(
        SAEnum(ClaimStatus, name="claim_status"), nullable=False, default=ClaimStatus.draft, index=True
    )
    damage_type = Column(SAEnum(DamageType, name="damage_type"), nullable=False)
    damage_description = Column(Text, nullable=True)
    estimated_loss = Column(Numeric(12, 2), nullable=True)
    affected_acres = Column(Numeric(8, 3), nullable=True)
    trust_score = Column(Numeric(5, 2), nullable=True)
    officer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    officer_notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    farm = relationship("Farm", back_populates="claims")
    farmer = relationship("User", foreign_keys=[farmer_id])
    officer = relationship("User", foreign_keys=[officer_id])
    images = relationship("ClaimImage", back_populates="claim", lazy="selectin")
    fraud_report = relationship(
        "FraudReport", back_populates="claim", uselist=False, lazy="noload"
    )


class ClaimImage(Base):
    __tablename__ = "claim_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    storage_path = Column(Text, nullable=False)
    storage_url = Column(Text, nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    image_hash = Column(String, nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    claim = relationship("Claim", back_populates="images")
