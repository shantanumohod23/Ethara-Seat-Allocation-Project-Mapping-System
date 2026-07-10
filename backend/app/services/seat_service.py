"""Seat domain service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.enums import AllocationStatus, SeatStatus
from app.models.seat import Seat
from app.models.seat_allocation import SeatAllocation
from app.schemas.seat import SeatCreate, SeatRead, SeatUpdate
from app.utils.pagination import calculate_offset, calculate_total_pages


@dataclass(frozen=True, slots=True)
class SeatListFilters:
    """Query parameters for listing seats."""

    page: int = 1
    page_size: int = 20
    floor: str | None = None
    zone: str | None = None
    bay: str | None = None
    status: SeatStatus | None = None
    sort_order: Literal["asc", "desc"] = "asc"


class SeatService:
    """Business logic for seat inventory."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_seats(self, filters: SeatListFilters) -> tuple[list[SeatRead], int]:
        query = select(Seat)
        count_query = select(func.count()).select_from(Seat)
        conditions = self._conditions(filters)
        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)
        order = Seat.floor.desc() if filters.sort_order == "desc" else Seat.floor.asc()
        query = query.order_by(order, Seat.zone.asc(), Seat.bay.asc(), Seat.seat_number.asc())
        query = query.offset(calculate_offset(filters.page, filters.page_size)).limit(
            filters.page_size,
        )
        total = (await self._db.execute(count_query)).scalar_one()
        seats = (await self._db.execute(query)).scalars().all()
        return [SeatRead.model_validate(seat) for seat in seats], total

    async def get_seat(self, seat_id: int) -> SeatRead:
        return SeatRead.model_validate(await self._get_or_raise(seat_id))

    async def create_seat(self, data: SeatCreate) -> SeatRead:
        seat = Seat(**data.model_dump())
        self._db.add(seat)
        try:
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise ConflictError("Seat already exists for this floor/zone/bay/number.") from exc
        await self._db.refresh(seat)
        return SeatRead.model_validate(seat)

    async def update_seat(self, seat_id: int, data: SeatUpdate) -> SeatRead:
        seat = await self._get_or_raise(seat_id)
        update_data = data.model_dump(exclude_unset=True)

        requested_status = update_data.get("status")
        if requested_status in {
            SeatStatus.AVAILABLE,
            SeatStatus.RESERVED,
            SeatStatus.MAINTENANCE,
        } and await self._has_active_allocation(seat.id):
            raise ConflictError(
                "Seat with an active allocation cannot be marked available, "
                "reserved, or maintenance. Release the allocation first.",
            )

        for field, value in update_data.items():
            setattr(seat, field, value)
        try:
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise ConflictError("Seat update conflicts with existing data.") from exc
        await self._db.refresh(seat)
        return SeatRead.model_validate(seat)

    async def available_seats(
        self,
        floor: str | None = None,
        zone: str | None = None,
        limit: int = 100,
    ) -> list[SeatRead]:
        query = select(Seat).where(Seat.status == SeatStatus.AVAILABLE)
        if floor:
            query = query.where(Seat.floor == floor)
        if zone:
            query = query.where(Seat.zone == zone)
        query = query.order_by(Seat.floor.asc(), Seat.zone.asc(), Seat.bay.asc()).limit(limit)
        seats = (await self._db.execute(query)).scalars().all()
        return [SeatRead.model_validate(seat) for seat in seats]

    async def _get_or_raise(self, seat_id: int) -> Seat:
        seat = (await self._db.execute(select(Seat).where(Seat.id == seat_id))).scalar_one_or_none()
        if seat is None:
            raise NotFoundError(f"Seat with id {seat_id} not found.")
        return seat

    async def _has_active_allocation(self, seat_id: int) -> bool:
        allocation_id = (
            await self._db.execute(
                select(SeatAllocation.id).where(
                    SeatAllocation.seat_id == seat_id,
                    SeatAllocation.status == AllocationStatus.ACTIVE,
                ),
            )
        ).scalar_one_or_none()
        return allocation_id is not None

    @staticmethod
    def _conditions(filters: SeatListFilters) -> list:
        conditions = []
        if filters.floor:
            conditions.append(Seat.floor == filters.floor)
        if filters.zone:
            conditions.append(Seat.zone == filters.zone)
        if filters.bay:
            conditions.append(Seat.bay == filters.bay)
        if filters.status is not None:
            conditions.append(Seat.status == filters.status)
        return conditions

    @staticmethod
    def build_list_response(items: list[SeatRead], total: int, filters: SeatListFilters) -> dict:
        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size,
            "total_pages": calculate_total_pages(total, filters.page_size),
        }
