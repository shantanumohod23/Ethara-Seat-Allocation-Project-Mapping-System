"""Project Pydantic schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProjectStatus
from app.schemas.common import PaginatedResponse


class ProjectBase(BaseModel):
    """Shared project fields."""

    project_code: str = Field(..., min_length=1, max_length=32, examples=["INDIGO"])
    name: str = Field(..., min_length=1, max_length=200, examples=["Indigo"])
    description: str | None = None
    manager_name: str | None = Field(None, max_length=200)
    status: ProjectStatus = ProjectStatus.ACTIVE
    start_date: date | None = None
    end_date: date | None = None


class ProjectCreate(ProjectBase):
    """Payload for creating a project."""


class ProjectUpdate(BaseModel):
    """Payload for updating a project."""

    project_code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    manager_name: str | None = Field(None, max_length=200)
    status: ProjectStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectRead(ProjectBase):
    """Project response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(PaginatedResponse[ProjectRead]):
    """Paginated project list."""


class ProjectEmployeeRead(BaseModel):
    """Compact employee row returned from a project membership lookup."""

    id: int
    employee_code: str
    name: str
    email: str
    department: str | None = None
    employment_status: str
