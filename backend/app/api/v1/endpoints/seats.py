"""Seat route handlers."""

from typing import Literal

from fastapi import APIRouter, Query, status

from app.api.deps import SeatServiceDep
from app.models.enums import SeatStatus
from app.schemas.seat import SeatCreate, SeatListResponse, SeatRead, SeatUpdate
from app.services.seat_service import SeatListFilters, SeatService

router = APIRouter(prefix="/seats", tags=["seats"])


@router.get("", response_model=SeatListResponse, summary="List seats")
async def list_seats(
    service: SeatServiceDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    floor: str | None = None,
    zone: str | None = None,
    bay: str | None = None,
    status: SeatStatus | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
) -> SeatListResponse:
    filters = SeatListFilters(
        page=page,
        page_size=page_size,
        floor=floor,
        zone=zone,
        bay=bay,
        status=status,
        sort_order=sort_order,
    )
    items, total = await service.list_seats(filters)
    return SeatListResponse(**SeatService.build_list_response(items, total, filters))


@router.get("/available", response_model=list[SeatRead], summary="List available seats")
async def list_available_seats(
    service: SeatServiceDep,
    floor: str | None = None,
    zone: str | None = None,
    limit: int = Query(100, ge=1, le=500),
) -> list[SeatRead]:
    return await service.available_seats(floor=floor, zone=zone, limit=limit)


@router.post("", response_model=SeatRead, status_code=status.HTTP_201_CREATED)
async def create_seat(payload: SeatCreate, service: SeatServiceDep) -> SeatRead:
    return await service.create_seat(payload)


@router.get("/{seat_id}", response_model=SeatRead, summary="Get seat details")
async def get_seat(seat_id: int, service: SeatServiceDep) -> SeatRead:
    return await service.get_seat(seat_id)


@router.put("/{seat_id}", response_model=SeatRead, summary="Update seat")
async def update_seat(seat_id: int, payload: SeatUpdate, service: SeatServiceDep) -> SeatRead:
    return await service.update_seat(seat_id, payload)
