"""Seat allocation Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AllocationStatus
from app.schemas.common import PaginatedResponse


class SeatAllocationCreate(BaseModel):
    """Payload for assigning a seat to an employee."""

    employee_id: int
    seat_id: int
    project_id: int | None = Field(
        None,
        description="Optional override; defaults to the employee's current project.",
    )
    notes: str | None = None


class SeatAllocationRelease(BaseModel):
    """Payload for releasing a seat allocation."""

    allocation_id: int | None = None
    employee_id: int | None = None
    seat_id: int | None = None
    notes: str | None = None


class SeatAllocationRead(BaseModel):
    """Seat allocation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    seat_id: int
    project_id: int
    status: AllocationStatus
    allocated_at: datetime
    released_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class SeatSuggestion(BaseModel):
    """Suggested seat with a simple proximity score."""

    seat: dict
    score: int
    reason: str


class SeatAllocationListResponse(PaginatedResponse[SeatAllocationRead]):
    """Paginated allocation list."""
