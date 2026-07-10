"""Employee Pydantic schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import EmploymentStatus
from app.schemas.common import PaginatedResponse


class EmployeeBase(BaseModel):
    """Shared employee fields for create and read operations."""

    employee_code: str = Field(
        ...,
        min_length=1,
        max_length=32,
        examples=["EMP-0042"],
        description="Internal workforce identifier; must be unique.",
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        examples=["jane.doe@example.com"],
        description="Corporate email; must be unique.",
    )
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    department: str | None = Field(None, max_length=100)
    job_title: str | None = Field(None, max_length=150)
    joining_date: date
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    project_id: int | None = Field(
        None,
        description="Current project assignment; must reference an existing project.",
    )


class EmployeeCreate(EmployeeBase):
    """Payload for creating a new employee."""


class EmployeeUpdate(BaseModel):
    """Payload for updating an employee; all fields are optional."""

    employee_code: str | None = Field(None, min_length=1, max_length=32)
    email: EmailStr | None = Field(None, max_length=255)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    department: str | None = Field(None, max_length=100)
    job_title: str | None = Field(None, max_length=150)
    joining_date: date | None = None
    employment_status: EmploymentStatus | None = None
    project_id: int | None = None


class EmployeeRead(EmployeeBase):
    """Employee response returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class EmployeeListResponse(PaginatedResponse[EmployeeRead]):
    """Paginated employee list response."""
