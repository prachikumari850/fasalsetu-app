from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import uuid
from app.models.user import UserRole


class SendOtpRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    preferred_lang: str = "hi"

    @field_validator("preferred_lang")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        if v not in ("en", "hi"):
            raise ValueError("preferred_lang must be 'en' or 'hi'")
        return v


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 8:
            raise ValueError("OTP must be exactly 8 digits")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    preferred_lang: str = "hi"


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


TokenResponse.model_rebuild()