"""FastAPI dependency injection helpers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.services.employee_service import EmployeeService
from app.services.project_service import ProjectService
from app.services.seat_allocation_service import SeatAllocationService
from app.services.seat_service import SeatService

DbSession = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_employee_service(db: DbSession) -> EmployeeService:
    """Provide a request-scoped employee service."""
    return EmployeeService(db)


def get_project_service(db: DbSession) -> ProjectService:
    """Provide a request-scoped project service."""
    return ProjectService(db)


def get_seat_service(db: DbSession) -> SeatService:
    """Provide a request-scoped seat service."""
    return SeatService(db)


def get_seat_allocation_service(db: DbSession) -> SeatAllocationService:
    """Provide a request-scoped allocation service."""
    return SeatAllocationService(db)


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
SeatServiceDep = Annotated[SeatService, Depends(get_seat_service)]
SeatAllocationServiceDep = Annotated[
    SeatAllocationService,
    Depends(get_seat_allocation_service),
]
