"""Seat allocation domain service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.employee import Employee
from app.models.enums import AllocationStatus, EmploymentStatus, SeatStatus
from app.models.project import Project
from app.models.seat import Seat
from app.models.seat_allocation import SeatAllocation
from app.schemas.seat_allocation import SeatAllocationCreate, SeatAllocationRead
from app.utils.pagination import calculate_offset, calculate_total_pages


@dataclass(frozen=True, slots=True)
class AllocationListFilters:
    """Query parameters for listing allocations."""

    page: int = 1
    page_size: int = 20
    employee_id: int | None = None
    seat_id: int | None = None
    project_id: int | None = None
    status: AllocationStatus | None = None


class SeatAllocationService:
    """Business logic for assigning and releasing seats."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_allocations(
        self,
        filters: AllocationListFilters,
    ) -> tuple[list[SeatAllocationRead], int]:
        query = select(SeatAllocation)
        count_query = select(func.count()).select_from(SeatAllocation)
        conditions = []
        if filters.employee_id is not None:
            conditions.append(SeatAllocation.employee_id == filters.employee_id)
        if filters.seat_id is not None:
            conditions.append(SeatAllocation.seat_id == filters.seat_id)
        if filters.project_id is not None:
            conditions.append(SeatAllocation.project_id == filters.project_id)
        if filters.status is not None:
            conditions.append(SeatAllocation.status == filters.status)
        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)

        query = (
            query.order_by(SeatAllocation.allocated_at.desc(), SeatAllocation.id.desc())
            .offset(calculate_offset(filters.page, filters.page_size))
            .limit(filters.page_size)
        )
        total = (await self._db.execute(count_query)).scalar_one()
        allocations = (await self._db.execute(query)).scalars().all()
        return [SeatAllocationRead.model_validate(row) for row in allocations], total

    async def allocate(self, data: SeatAllocationCreate) -> SeatAllocationRead:
        employee = await self._get_employee(data.employee_id)
        seat = await self._get_seat(data.seat_id)
        project_id = data.project_id or employee.project_id

        if project_id is None:
            raise ConflictError("Employee must be assigned to a project before seat allocation.")
        await self._ensure_project(project_id)
        if employee.employment_status not in {
            EmploymentStatus.ACTIVE,
            EmploymentStatus.ONBOARDING,
        }:
            raise ConflictError("Only active or onboarding employees can receive seats.")
        if seat.status != SeatStatus.AVAILABLE:
            raise ConflictError("Only available seats can be allocated.")

        await self._ensure_no_active_employee_allocation(employee.id)
        await self._ensure_no_active_seat_allocation(seat.id)

        allocation = SeatAllocation(
            employee_id=employee.id,
            seat_id=seat.id,
            project_id=project_id,
            status=AllocationStatus.ACTIVE,
            notes=data.notes,
        )
        self._db.add(allocation)
        try:
            await self._db.flush()
            seat.status = SeatStatus.OCCUPIED
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise ConflictError("Seat allocation conflicts with existing active allocation.") from exc
        await self._db.refresh(allocation)
        return SeatAllocationRead.model_validate(allocation)

    async def release(self, allocation_id: int, notes: str | None = None) -> SeatAllocationRead:
        allocation = await self._get_allocation(allocation_id)
        return await self._release_allocation(allocation, notes)

    async def release_matching(
        self,
        *,
        allocation_id: int | None = None,
        employee_id: int | None = None,
        seat_id: int | None = None,
        notes: str | None = None,
    ) -> SeatAllocationRead:
        """Release an active allocation by allocation, employee, or seat id."""
        if allocation_id is not None:
            return await self.release(allocation_id, notes)
        conditions = [SeatAllocation.status == AllocationStatus.ACTIVE]
        if employee_id is not None:
            conditions.append(SeatAllocation.employee_id == employee_id)
        if seat_id is not None:
            conditions.append(SeatAllocation.seat_id == seat_id)
        if len(conditions) == 1:
            raise ConflictError("Provide allocation_id, employee_id, or seat_id to release a seat.")
        allocation = (
            await self._db.execute(select(SeatAllocation).where(*conditions).limit(1))
        ).scalar_one_or_none()
        if allocation is None:
            raise NotFoundError("No active allocation found for the release request.")
        return await self._release_allocation(allocation, notes)

    async def _release_allocation(
        self,
        allocation: SeatAllocation,
        notes: str | None = None,
    ) -> SeatAllocationRead:
        if allocation.status != AllocationStatus.ACTIVE:
            raise ConflictError("Only active allocations can be released.")

        seat = await self._get_seat(allocation.seat_id)
        allocation.status = AllocationStatus.RELEASED
        allocation.released_at = datetime.now(timezone.utc)
        allocation.notes = notes or allocation.notes
        if seat.status not in {SeatStatus.MAINTENANCE, SeatStatus.RESERVED}:
            seat.status = SeatStatus.AVAILABLE
        await self._db.commit()
        await self._db.refresh(allocation)
        return SeatAllocationRead.model_validate(allocation)

    async def suggest_for_employee(self, employee_id: int, limit: int = 5) -> list[dict]:
        employee = await self._get_employee(employee_id)
        project_id = employee.project_id

        preferred = None
        if project_id is not None:
            preferred = (
                await self._db.execute(
                    select(Seat.floor, Seat.zone, func.count().label("count"))
                    .join(SeatAllocation, SeatAllocation.seat_id == Seat.id)
                    .where(
                        SeatAllocation.project_id == project_id,
                        SeatAllocation.status == AllocationStatus.ACTIVE,
                    )
                    .group_by(Seat.floor, Seat.zone)
                    .order_by(func.count().desc()),
                )
            ).first()

        query = select(Seat).where(Seat.status == SeatStatus.AVAILABLE)
        seats = (await self._db.execute(query.limit(200))).scalars().all()
        suggestions = []
        for seat in seats:
            score = 10
            reasons = ["available"]
            if preferred and seat.floor == preferred.floor:
                score += 20
                reasons.append(f"same floor as project team ({seat.floor})")
            if preferred and seat.zone == preferred.zone:
                score += 30
                reasons.append(f"same zone as project team ({seat.zone})")
            suggestions.append(
                {
                    "seat": {
                        "id": seat.id,
                        "floor": seat.floor,
                        "zone": seat.zone,
                        "bay": seat.bay,
                        "seat_number": seat.seat_number,
                        "status": seat.status,
                    },
                    "score": score,
                    "reason": ", ".join(reasons),
                },
            )
        suggestions.sort(key=lambda item: item["score"], reverse=True)
        return suggestions[:limit]

    async def _get_employee(self, employee_id: int) -> Employee:
        employee = (
            await self._db.execute(select(Employee).where(Employee.id == employee_id))
        ).scalar_one_or_none()
        if employee is None:
            raise NotFoundError(f"Employee with id {employee_id} not found.")
        return employee

    async def _get_seat(self, seat_id: int) -> Seat:
        seat = (await self._db.execute(select(Seat).where(Seat.id == seat_id))).scalar_one_or_none()
        if seat is None:
            raise NotFoundError(f"Seat with id {seat_id} not found.")
        return seat

    async def _get_allocation(self, allocation_id: int) -> SeatAllocation:
        allocation = (
            await self._db.execute(
                select(SeatAllocation).where(SeatAllocation.id == allocation_id),
            )
        ).scalar_one_or_none()
        if allocation is None:
            raise NotFoundError(f"Allocation with id {allocation_id} not found.")
        return allocation

    async def _ensure_project(self, project_id: int) -> None:
        project = (
            await self._db.execute(select(Project.id).where(Project.id == project_id))
        ).scalar_one_or_none()
        if project is None:
            raise NotFoundError(f"Project with id {project_id} not found.")

    async def _ensure_no_active_employee_allocation(self, employee_id: int) -> None:
        existing = (
            await self._db.execute(
                select(SeatAllocation.id).where(
                    SeatAllocation.employee_id == employee_id,
                    SeatAllocation.status == AllocationStatus.ACTIVE,
                ),
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise ConflictError("Employee already has an active seat allocation.")

    async def _ensure_no_active_seat_allocation(self, seat_id: int) -> None:
        existing = (
            await self._db.execute(
                select(SeatAllocation.id).where(
                    SeatAllocation.seat_id == seat_id,
                    SeatAllocation.status == AllocationStatus.ACTIVE,
                ),
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise ConflictError("Seat already has an active allocation.")

    @staticmethod
    def build_list_response(
        items: list[SeatAllocationRead],
        total: int,
        filters: AllocationListFilters,
    ) -> dict:
        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size,
            "total_pages": calculate_total_pages(total, filters.page_size),
        }
