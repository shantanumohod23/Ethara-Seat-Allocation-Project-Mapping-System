"""AI route handlers."""

from __future__ import annotations

import re
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession
from app.models.employee import Employee
from app.models.enums import AllocationStatus, EmploymentStatus, SeatStatus
from app.models.project import Project
from app.models.seat import Seat
from app.models.seat_allocation import SeatAllocation
from app.schemas.seat_allocation import SeatAllocationCreate
from app.services.seat_allocation_service import SeatAllocationService

router = APIRouter(prefix="/ai", tags=["ai"])


class AiQueryRequest(BaseModel):
    """Natural-language assistant request."""

    query: str = Field(..., min_length=1, examples=["Where is my seat? My email is amit@ethara.ai"])


class AiQueryResponse(BaseModel):
    """Natural-language assistant response."""

    answer: str
    intent: str


@router.post("/query", response_model=AiQueryResponse, summary="Rule-based AI assistant")
async def query_assistant(payload: AiQueryRequest, db: DbSession) -> AiQueryResponse:
    query = payload.query.strip()
    lowered = query.lower()

    email = _extract_email(query)
    if _is_new_joiner_allocation_query(lowered):
        answer = await _allocate_new_joiner_today_answer(db)
        return AiQueryResponse(answer=answer, intent="new_joiner_allocation")

    if "project" in lowered and ("assigned" in lowered or "assignment" in lowered):
        if _is_self_reference(lowered) and not _has_identity_hint(query, email):
            return _identity_required_response("project_assignment")
        employee = await _find_employee(db, query, email)
        if employee:
            answer = await _project_assignment_answer(db, employee)
            return AiQueryResponse(answer=answer, intent="project_assignment")

    if "who" in lowered and ("near me" in lowered or "sitting near" in lowered):
        if _is_self_reference(lowered) and not _has_identity_hint(query, email):
            return _identity_required_response("nearby_seats")
        employee = await _find_employee(db, query, email)
        if employee:
            answer = await _nearby_seats_answer(db, employee)
            return AiQueryResponse(answer=answer, intent="nearby_seats")

    if email or "where" in lowered and "seat" in lowered:
        if _is_self_reference(lowered) and not _has_identity_hint(query, email):
            return _identity_required_response("employee_seat")
        employee = await _find_employee(db, query, email)
        if employee:
            answer = await _seat_answer(db, employee)
            return AiQueryResponse(answer=answer, intent="employee_seat")

    if "available" in lowered and "seat" in lowered:
        floor = _extract_after(query, "floor")
        statement = select(Seat).where(Seat.status == SeatStatus.AVAILABLE)
        if floor:
            statement = statement.where(func.lower(Seat.floor) == floor.lower())
        seats = (await db.execute(statement.limit(10))).scalars().all()
        if not seats:
            scope = f" on Floor {floor}" if floor else ""
            return AiQueryResponse(answer=f"No available seats found{scope}.", intent="available_seats")
        rendered = ", ".join(
            f"Floor {seat.floor}, {seat.zone}, {seat.bay}, Seat {seat.seat_number}"
            for seat in seats
        )
        return AiQueryResponse(answer=f"Available seats: {rendered}.", intent="available_seats")

    if "how many" in lowered and "project" in lowered:
        project_name = _extract_project_name(query)
        project = await _find_project(db, project_name)
        if project:
            count = (
                await db.execute(
                    select(func.count()).where(
                        SeatAllocation.project_id == project.id,
                        SeatAllocation.status == AllocationStatus.ACTIVE,
                    ),
                )
            ).scalar_one()
            return AiQueryResponse(
                answer=f"Project {project.name} currently has {count} occupied seats.",
                intent="project_utilization",
            )

    return AiQueryResponse(
        answer=(
            "I can answer seat, project, available-seat, and utilization questions. "
            "Try: 'Where is employee Amit seated?' or 'Show available seats on Floor 3.'"
        ),
        intent="fallback",
    )


async def _find_employee(db: DbSession, query: str, email: str | None) -> Employee | None:
    statement = select(Employee)
    if email:
        statement = statement.where(func.lower(Employee.email) == email.lower())
    else:
        code_match = re.search(r"\b[A-Za-z]+[-_]?\d+\b", query)
        if code_match:
            code_pattern = f"%{code_match.group(0)}%"
            statement = statement.where(Employee.employee_code.ilike(code_pattern))
            return (await db.execute(statement.limit(1))).scalar_one_or_none()

        tokens = [
            token
            for token in re.findall(r"[A-Za-z0-9._-]+", query)
            if token.lower()
            not in {
                "where",
                "is",
                "employee",
                "seated",
                "seat",
                "my",
                "the",
                "for",
                "which",
                "project",
                "am",
                "assigned",
                "to",
                "who",
                "sitting",
                "near",
                "me",
            }
        ]
        if not tokens:
            return None
        pattern = f"%{tokens[-1]}%"
        statement = statement.where(
            or_(Employee.first_name.ilike(pattern), Employee.last_name.ilike(pattern)),
        )
    return (await db.execute(statement.limit(1))).scalar_one_or_none()


async def _seat_answer(db: DbSession, employee: Employee) -> str:
    allocation = (
        await db.execute(
            select(SeatAllocation)
            .options(selectinload(SeatAllocation.seat), selectinload(SeatAllocation.project))
            .where(
                SeatAllocation.employee_id == employee.id,
                SeatAllocation.status == AllocationStatus.ACTIVE,
            ),
        )
    ).scalar_one_or_none()
    name = f"{employee.first_name} {employee.last_name}"
    if allocation is None:
        return f"{name} does not currently have an active seat allocation."
    seat = allocation.seat
    project = allocation.project
    return (
        f"{name} is seated on Floor {seat.floor}, {seat.zone}, {seat.bay}, "
        f"Seat {seat.seat_number}. They are assigned to Project {project.name}."
    )


async def _project_assignment_answer(db: DbSession, employee: Employee) -> str:
    name = f"{employee.first_name} {employee.last_name}"
    if employee.project_id is None:
        return f"{name} is not currently assigned to a project."

    project = (
        await db.execute(select(Project).where(Project.id == employee.project_id))
    ).scalar_one_or_none()
    if project is None:
        return f"{name} has a project id assigned, but the project record was not found."

    return f"{name} is assigned to Project {project.name}."


async def _nearby_seats_answer(db: DbSession, employee: Employee) -> str:
    current_allocation = (
        await db.execute(
            select(SeatAllocation)
            .options(selectinload(SeatAllocation.seat))
            .where(
                SeatAllocation.employee_id == employee.id,
                SeatAllocation.status == AllocationStatus.ACTIVE,
            ),
        )
    ).scalar_one_or_none()
    name = f"{employee.first_name} {employee.last_name}"
    if current_allocation is None:
        return f"{name} does not currently have an active seat allocation, so I cannot find nearby employees."

    seat = current_allocation.seat
    nearby_allocations = (
        await db.execute(
            select(SeatAllocation)
            .join(Seat, SeatAllocation.seat_id == Seat.id)
            .options(
                selectinload(SeatAllocation.employee),
                selectinload(SeatAllocation.seat),
                selectinload(SeatAllocation.project),
            )
            .where(
                SeatAllocation.status == AllocationStatus.ACTIVE,
                SeatAllocation.employee_id != employee.id,
                Seat.floor == seat.floor,
                Seat.zone == seat.zone,
            )
            .order_by(
                (Seat.bay == seat.bay).desc(),
                Seat.bay.asc(),
                Seat.seat_number.asc(),
            )
            .limit(5),
        )
    ).scalars().all()

    if not nearby_allocations:
        return (
            f"No active neighbors were found near {name} on Floor {seat.floor}, "
            f"{seat.zone}."
        )

    neighbors = ", ".join(
        f"{allocation.employee.first_name} {allocation.employee.last_name} "
        f"at {allocation.seat.bay} Seat {allocation.seat.seat_number} "
        f"({allocation.project.name})"
        for allocation in nearby_allocations
    )
    return f"Employees sitting near {name} on Floor {seat.floor}, {seat.zone}: {neighbors}."


async def _find_project(db: DbSession, name: str) -> Project | None:
    if not name:
        return None
    pattern = f"%{name.strip()}%"
    return (
        await db.execute(select(Project).where(Project.name.ilike(pattern)).limit(1))
    ).scalar_one_or_none()


async def _allocate_new_joiner_today_answer(db: DbSession) -> str:
    employee = (
        await db.execute(
            select(Employee)
            .outerjoin(
                SeatAllocation,
                (SeatAllocation.employee_id == Employee.id)
                & (SeatAllocation.status == AllocationStatus.ACTIVE),
            )
            .where(
                Employee.employment_status == EmploymentStatus.ONBOARDING,
                Employee.joining_date == date.today(),
                SeatAllocation.id.is_(None),
            )
            .order_by(Employee.id.asc())
            .limit(1),
        )
    ).scalar_one_or_none()
    if employee is None:
        return (
            "I could not find an onboarding employee joining today who is "
            "pending seat allocation."
        )

    allocation_service = SeatAllocationService(db)
    suggestions = await allocation_service.suggest_for_employee(employee.id, limit=1)
    if not suggestions:
        return (
            f"{employee.first_name} {employee.last_name} is joining today, "
            "but no available seats were found."
        )

    seat = suggestions[0]["seat"]
    allocation = await allocation_service.allocate(
        SeatAllocationCreate(
            employee_id=employee.id,
            seat_id=seat["id"],
            project_id=employee.project_id,
            notes="Allocated by rule-based AI assistant for new joiner.",
        ),
    )
    allocated_seat = await db.get(Seat, allocation.seat_id)
    if allocated_seat is None:
        return (
            f"Allocated a seat to {employee.first_name} {employee.last_name}, "
            "but the seat details could not be loaded."
        )

    return (
        f"Allocated {employee.first_name} {employee.last_name} to Floor "
        f"{allocated_seat.floor}, {allocated_seat.zone}, {allocated_seat.bay}, "
        f"Seat {allocated_seat.seat_number}."
    )


def _identity_required_response(intent: str) -> AiQueryResponse:
    return AiQueryResponse(
        answer=(
            "Please provide an employee email or employee name so I can answer "
            "that question."
        ),
        intent=intent,
    )


def _is_self_reference(lowered: str) -> bool:
    return bool(re.search(r"\b(my|me|i)\b", lowered))


def _has_identity_hint(text: str, email: str | None) -> bool:
    if email:
        return True
    tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z]+", text)
        if token.lower()
        not in {
            "where",
            "is",
            "employee",
            "seated",
            "seat",
            "my",
            "the",
            "for",
            "which",
            "project",
            "am",
            "assigned",
            "assignment",
            "to",
            "who",
            "sitting",
            "near",
            "me",
            "i",
        }
    ]
    return bool(tokens)


def _extract_project_name(text: str) -> str:
    match = re.search(r"\bproject\s+(.+)$", text, flags=re.IGNORECASE)
    return match.group(1).strip(" ?.") if match else ""


def _is_new_joiner_allocation_query(lowered: str) -> bool:
    return (
        "allocate" in lowered
        and "seat" in lowered
        and (
            "new employee" in lowered
            or "new joiner" in lowered
            or "joining today" in lowered
        )
    )


def _extract_email(text: str) -> str | None:
    match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
    return match.group(0) if match else None


def _extract_after(text: str, word: str) -> str | None:
    match = re.search(rf"{word}\s+([A-Za-z0-9-]+)", text, flags=re.IGNORECASE)
    return match.group(1) if match else None
