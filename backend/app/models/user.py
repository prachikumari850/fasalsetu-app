from sqlalchemy import Column, String, Boolean, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
from app.models.base import Base
import enum


class UserRole(str, enum.Enum):
    farmer = "farmer"
    officer = "officer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.farmer)
    district = Column(String, nullable=True)
    state = Column(String, nullable=False, default="Uttar Pradesh")
    profile_url = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    preferred_lang = Column(String(5), nullable=False, default="hi")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    farms = relationship("Farm", back_populates="owner", lazy="selectin")
    notifications = relationship("Notification", back_populates="user", lazy="noload")