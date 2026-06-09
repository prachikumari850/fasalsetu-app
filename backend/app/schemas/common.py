from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, Any
from datetime import datetime
import uuid

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    total: int
    page: int
    per_page: int
    has_next: bool


class ErrorResponse(BaseModel):
    success: bool = False
    code: str
    detail: Any