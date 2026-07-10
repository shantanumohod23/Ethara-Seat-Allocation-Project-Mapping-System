"""Seat Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SeatStatus
from app.schemas.common import PaginatedResponse


class SeatBase(BaseModel):
    """Shared seat fields."""

    floor: str = Field(..., min_length=1, max_length=20, examples=["2"])
    zone: str = Field(..., min_length=1, max_length=50, examples=["Zone B"])
    bay: str = Field(..., min_length=1, max_length=50, examples=["Bay 4"])
    seat_number: str = Field(..., min_length=1, max_length=20, examples=["B4-23"])
    status: SeatStatus = SeatStatus.AVAILABLE


class SeatCreate(SeatBase):
    """Payload for creating a seat."""


class SeatUpdate(BaseModel):
    """Payload for updating a seat."""

    floor: str | None = Field(None, min_length=1, max_length=20)
    zone: str | None = Field(None, min_length=1, max_length=50)
    bay: str | None = Field(None, min_length=1, max_length=50)
    seat_number: str | None = Field(None, min_length=1, max_length=20)
    status: SeatStatus | None = None


class SeatRead(SeatBase):
    """Seat response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SeatListResponse(PaginatedResponse[SeatRead]):
    """Paginated seat list."""
