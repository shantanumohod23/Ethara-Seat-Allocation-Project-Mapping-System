"""Dashboard route handlers."""

from fastapi import APIRouter
from sqlalchemy import case, func, select

from app.api.deps import DbSession
from app.models.employee import Employee
from app.models.enums import AllocationStatus, EmploymentStatus, SeatStatus
from app.models.project import Project
from app.models.seat import Seat
from app.models.seat_allocation import SeatAllocation

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=dict, summary="Dashboard summary")
async def summary(db: DbSession) -> dict:
    total_employees = (await db.execute(select(func.count()).select_from(Employee))).scalar_one()
    total_seats = (await db.execute(select(func.count()).select_from(Seat))).scalar_one()
    occupied_seats = (
        await db.execute(select(func.count()).where(Seat.status == SeatStatus.OCCUPIED))
    ).scalar_one()
    available_seats = (
        await db.execute(select(func.count()).where(Seat.status == SeatStatus.AVAILABLE))
    ).scalar_one()
    reserved_seats = (
        await db.execute(select(func.count()).where(Seat.status == SeatStatus.RESERVED))
    ).scalar_one()
    pending_new_joiners = (
        await db.execute(
            select(func.count())
            .select_from(Employee)
            .outerjoin(
                SeatAllocation,
                (SeatAllocation.employee_id == Employee.id)
                & (SeatAllocation.status == AllocationStatus.ACTIVE),
            )
            .where(
                Employee.employment_status == EmploymentStatus.ONBOARDING,
                SeatAllocation.id.is_(None),
            ),
        )
    ).scalar_one()
    return {
        "total_employees": total_employees,
        "total_seats": total_seats,
        "occupied_seats": occupied_seats,
        "available_seats": available_seats,
        "reserved_seats": reserved_seats,
        "new_joiners_pending_allocation": pending_new_joiners,
    }


@router.get(
    "/project-utilization",
    response_model=list[dict],
    summary="Project-wise allocation",
)
async def project_utilization(db: DbSession) -> list[dict]:
    result = await db.execute(
        select(
            Project.id,
            Project.name,
            func.count(SeatAllocation.id).label("occupied_seats"),
        )
        .outerjoin(
            SeatAllocation,
            (SeatAllocation.project_id == Project.id)
            & (SeatAllocation.status == AllocationStatus.ACTIVE),
        )
        .group_by(Project.id, Project.name)
        .order_by(func.count(SeatAllocation.id).desc(), Project.name.asc()),
    )
    return [
        {"project_id": row.id, "project_name": row.name, "occupied_seats": row.occupied_seats}
        for row in result.all()
    ]


@router.get(
    "/floor-utilization",
    response_model=list[dict],
    summary="Floor-wise occupancy",
)
async def floor_utilization(db: DbSession) -> list[dict]:
    occupied = case((Seat.status == SeatStatus.OCCUPIED, 1), else_=0)
    available = case((Seat.status == SeatStatus.AVAILABLE, 1), else_=0)
    reserved = case((Seat.status == SeatStatus.RESERVED, 1), else_=0)
    result = await db.execute(
        select(
            Seat.floor,
            func.count(Seat.id).label("total_seats"),
            func.sum(occupied).label("occupied_seats"),
            func.sum(available).label("available_seats"),
            func.sum(reserved).label("reserved_seats"),
        )
        .group_by(Seat.floor)
        .order_by(Seat.floor.asc()),
    )
    return [
        {
            "floor": row.floor,
            "total_seats": row.total_seats,
            "occupied_seats": row.occupied_seats or 0,
            "available_seats": row.available_seats or 0,
            "reserved_seats": row.reserved_seats or 0,
            "occupancy_percent": round(
                ((row.occupied_seats or 0) / row.total_seats) * 100,
                2,
            )
            if row.total_seats
            else 0,
        }
        for row in result.all()
    ]
