"""Seat allocation route handlers."""

from fastapi import APIRouter, Query, status

from app.api.deps import SeatAllocationServiceDep
from app.models.enums import AllocationStatus
from app.schemas.seat_allocation import (
    SeatAllocationCreate,
    SeatAllocationListResponse,
    SeatAllocationRead,
    SeatAllocationRelease,
)
from app.services.seat_allocation_service import (
    AllocationListFilters,
    SeatAllocationService,
)

router = APIRouter(prefix="/seats", tags=["seat allocations"])
alias_router = APIRouter(tags=["seat allocations"])


@router.post(
    "/allocate",
    response_model=SeatAllocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Allocate seat",
)
async def allocate_seat(
    payload: SeatAllocationCreate,
    service: SeatAllocationServiceDep,
) -> SeatAllocationRead:
    return await service.allocate(payload)


@alias_router.post(
    "/allocate",
    response_model=SeatAllocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Allocate seat",
)
async def allocate_seat_alias(
    payload: SeatAllocationCreate,
    service: SeatAllocationServiceDep,
) -> SeatAllocationRead:
    return await service.allocate(payload)


@router.post(
    "/release",
    response_model=SeatAllocationRead,
    summary="Release seat",
)
async def release_seat_by_body(
    payload: SeatAllocationRelease,
    service: SeatAllocationServiceDep,
) -> SeatAllocationRead:
    return await service.release_matching(
        allocation_id=payload.allocation_id,
        employee_id=payload.employee_id,
        seat_id=payload.seat_id,
        notes=payload.notes,
    )


@alias_router.post(
    "/release",
    response_model=SeatAllocationRead,
    summary="Release seat",
)
async def release_seat_by_body_alias(
    payload: SeatAllocationRelease,
    service: SeatAllocationServiceDep,
) -> SeatAllocationRead:
    return await service.release_matching(
        allocation_id=payload.allocation_id,
        employee_id=payload.employee_id,
        seat_id=payload.seat_id,
        notes=payload.notes,
    )


@router.post(
    "/release/{allocation_id}",
    response_model=SeatAllocationRead,
    summary="Release seat",
)
async def release_seat(
    allocation_id: int,
    payload: SeatAllocationRelease,
    service: SeatAllocationServiceDep,
) -> SeatAllocationRead:
    return await service.release(allocation_id, payload.notes)


@router.get(
    "/suggestions/{employee_id}",
    response_model=list[dict],
    summary="Suggest available seats for a new joiner or employee",
)
async def suggest_seats(
    employee_id: int,
    service: SeatAllocationServiceDep,
    limit: int = Query(5, ge=1, le=25),
) -> list[dict]:
    return await service.suggest_for_employee(employee_id, limit)


@router.get(
    "/allocations",
    response_model=SeatAllocationListResponse,
    summary="List seat allocations",
)
async def list_allocations(
    service: SeatAllocationServiceDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: int | None = None,
    seat_id: int | None = None,
    project_id: int | None = None,
    status: AllocationStatus | None = None,
) -> SeatAllocationListResponse:
    filters = AllocationListFilters(
        page=page,
        page_size=page_size,
        employee_id=employee_id,
        seat_id=seat_id,
        project_id=project_id,
        status=status,
    )
    items, total = await service.list_allocations(filters)
    return SeatAllocationListResponse(
        **SeatAllocationService.build_list_response(items, total, filters),
    )
