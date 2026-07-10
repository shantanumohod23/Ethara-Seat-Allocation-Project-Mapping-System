"""Shared Pydantic schema primitives (pagination, timestamps, etc.)."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standard offset pagination query parameters."""

    page: int = Field(1, ge=1, description="1-based page number.")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page.")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response envelope."""

    items: list[T]
    total: int = Field(..., ge=0, description="Total number of matching records.")
    page: int = Field(..., ge=1, description="Current page number.")
    page_size: int = Field(..., ge=1, description="Items returned per page.")
    total_pages: int = Field(..., ge=0, description="Total number of pages.")


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str = Field(..., examples=["healthy"])
    database: str = Field(..., examples=["connected"])
    version: str = Field(..., examples=["1.0.0"])


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    detail: str | list | dict
