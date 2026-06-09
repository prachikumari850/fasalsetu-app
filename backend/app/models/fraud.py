from sqlalchemy import Column, Numeric, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
from app.models.base import Base


class FraudReport(Base):
    __tablename__ = "fraud_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    gps_score = Column(Numeric(5, 2), nullable=False, default=0)
    lifecycle_score = Column(Numeric(5, 2), nullable=False, default=0)
    weather_score = Column(Numeric(5, 2), nullable=False, default=0)
    hash_score = Column(Numeric(5, 2), nullable=False, default=0)
    document_score = Column(Numeric(5, 2), nullable=False, default=0)
    total_fraud_score = Column(Numeric(5, 2), nullable=False, default=0)
    flags = Column(JSONB, nullable=False, default=list)
    weather_data = Column(JSONB, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    claim = relationship("Claim", back_populates="fraud_report")


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score = Column(Numeric(5, 2), nullable=False)
    grade = Column(String(1), nullable=False)
    breakdown = Column(JSONB, nullable=False, default=dict)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="trust_scores")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String, nullable=True)
    audit_metadata = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())