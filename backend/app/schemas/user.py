from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import uuid
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    preferred_lang: str = "hi"

    @field_validator("preferred_lang")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        if v not in ("en", "hi"):
            raise ValueError("preferred_lang must be 'en' or 'hi'")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    district: Optional[str] = None
    preferred_lang: Optional[str] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    district: Optional[str]
    state: str
    is_active: bool
    preferred_lang: str
    created_at: datetime

    model_config = {"from_attributes": True}