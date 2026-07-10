"""Employee route handlers."""

from typing import Literal

from fastapi import APIRouter, Query, status

from app.api.deps import EmployeeServiceDep
from app.models.enums import EmploymentStatus
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeRead,
    EmployeeUpdate,
)
from app.services.employee_service import (
    DEFAULT_SORT_BY,
    EmployeeListFilters,
    EmployeeService,
    SORTABLE_FIELDS,
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "",
    response_model=EmployeeListResponse,
    summary="List employees",
    description=(
        "Return a paginated list of employees with optional filtering, "
        "search, and sorting. Inactive (soft-deleted) employees are excluded "
        "by default; set `include_inactive=true` to include them."
    ),
)
async def list_employees(
    service: EmployeeServiceDep,
    page: int = Query(1, ge=1, description="1-based page number."),
    page_size: int = Query(20, ge=1, le=100, description="Items per page."),
    include_inactive: bool = Query(
        False,
        description=(
            "When true, include employees with employment_status=inactive. "
            "Defaults to false so soft-deleted employees are hidden."
        ),
    ),
    name: str | None = Query(
        None,
        description="Filter by first name, last name, or full name (partial match).",
    ),
    email: str | None = Query(
        None,
        description="Filter by email (partial match).",
    ),
    department: str | None = Query(
        None,
        description="Filter by department (partial match).",
    ),
    status: EmploymentStatus | None = Query(
        None,
        description="Filter by employment status.",
    ),
    search: str | None = Query(
        None,
        description=(
            "Search across employee code, email, name, department, and job title."
        ),
    ),
    sort_by: str = Query(
        DEFAULT_SORT_BY,
        description=f"Sort field. Allowed: {', '.join(sorted(SORTABLE_FIELDS))}.",
    ),
    sort_order: Literal["asc", "desc"] = Query(
        "asc",
        description="Sort direction.",
    ),
) -> EmployeeListResponse:
    """List employees with pagination, filtering, search, and sorting."""
    filters = EmployeeListFilters(
        page=page,
        page_size=page_size,
        name=name,
        email=email,
        department=department,
        status=status,
        search=search,
        include_inactive=include_inactive,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items, total = await service.list_employees(filters)
    return EmployeeListResponse(
        **EmployeeService.build_list_response(items, total, filters),
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Get employee by ID",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Employee not found."}},
)
async def get_employee(
    employee_id: int,
    service: EmployeeServiceDep,
) -> EmployeeRead:
    """Return a single employee by primary key."""
    return await service.get_employee(employee_id)


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create employee",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Email or employee code already exists.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Referenced project not found.",
        },
    },
)
async def create_employee(
    payload: EmployeeCreate,
    service: EmployeeServiceDep,
) -> EmployeeRead:
    """Create a new employee."""
    return await service.create_employee(payload)


@router.put(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Update employee",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Employee or project not found."},
        status.HTTP_409_CONFLICT: {
            "description": "Email or employee code already exists.",
        },
    },
)
async def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    service: EmployeeServiceDep,
) -> EmployeeRead:
    """Update an existing employee."""
    return await service.update_employee(employee_id, payload)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate employee",
    description=(
        "Soft-delete an employee by setting `employment_status` to `inactive`. "
        "The record and all seat allocation history are preserved. "
        "Calling this endpoint on an already inactive employee is a no-op."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Employee not found."},
    },
)
async def delete_employee(
    employee_id: int,
    service: EmployeeServiceDep,
) -> None:
    """Deactivate an employee (soft delete)."""
    await service.delete_employee(employee_id)
