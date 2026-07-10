"""Employee domain service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.employee import Employee
from app.models.enums import EmploymentStatus
from app.models.project import Project
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.utils.pagination import calculate_offset, calculate_total_pages

SORTABLE_FIELDS: dict[str, object] = {
    "employee_code": Employee.employee_code,
    "email": Employee.email,
    "first_name": Employee.first_name,
    "last_name": Employee.last_name,
    "department": Employee.department,
    "job_title": Employee.job_title,
    "joining_date": Employee.joining_date,
    "employment_status": Employee.employment_status,
    "created_at": Employee.created_at,
    "updated_at": Employee.updated_at,
}

DEFAULT_SORT_BY = "last_name"
DEFAULT_SORT_ORDER: Literal["asc", "desc"] = "asc"


@dataclass(frozen=True, slots=True)
class EmployeeListFilters:
    """Query parameters for listing employees."""

    page: int = 1
    page_size: int = 20
    name: str | None = None
    email: str | None = None
    department: str | None = None
    status: EmploymentStatus | None = None
    search: str | None = None
    include_inactive: bool = False
    sort_by: str = DEFAULT_SORT_BY
    sort_order: Literal["asc", "desc"] = DEFAULT_SORT_ORDER


class EmployeeService:
    """Business logic for employee CRUD and search."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_employees(
        self,
        filters: EmployeeListFilters,
    ) -> tuple[list[EmployeeRead], int]:
        """Return a paginated, filtered, sorted list of employees."""
        query = select(Employee)
        count_query = select(func.count()).select_from(Employee)

        conditions = self._build_filter_conditions(filters)
        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)

        sort_column = SORTABLE_FIELDS.get(filters.sort_by, Employee.last_name)
        if filters.sort_order == "desc":
            query = query.order_by(sort_column.desc(), Employee.id.asc())
        else:
            query = query.order_by(sort_column.asc(), Employee.id.asc())

        offset = calculate_offset(filters.page, filters.page_size)
        query = query.offset(offset).limit(filters.page_size)

        total = (await self._db.execute(count_query)).scalar_one()
        result = await self._db.execute(query)
        employees = result.scalars().all()

        return [EmployeeRead.model_validate(employee) for employee in employees], total

    async def get_employee(self, employee_id: int) -> EmployeeRead:
        """Return a single employee by ID."""
        employee = await self._get_or_raise(employee_id)
        return EmployeeRead.model_validate(employee)

    async def create_employee(self, data: EmployeeCreate) -> EmployeeRead:
        """Create a new employee after validating uniqueness and references."""
        await self._ensure_unique_email(data.email)
        await self._ensure_unique_employee_code(data.employee_code)
        if data.project_id is not None:
            await self._ensure_project_exists(data.project_id)

        employee = Employee(**data.model_dump())
        self._db.add(employee)

        try:
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise self._map_integrity_error(exc) from exc

        await self._db.refresh(employee)
        return EmployeeRead.model_validate(employee)

    async def update_employee(
        self,
        employee_id: int,
        data: EmployeeUpdate,
    ) -> EmployeeRead:
        """Update an existing employee."""
        employee = await self._get_or_raise(employee_id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return EmployeeRead.model_validate(employee)

        if "email" in update_data and update_data["email"] != employee.email:
            await self._ensure_unique_email(update_data["email"], exclude_id=employee_id)

        if (
            "employee_code" in update_data
            and update_data["employee_code"] != employee.employee_code
        ):
            await self._ensure_unique_employee_code(
                update_data["employee_code"],
                exclude_id=employee_id,
            )

        if "project_id" in update_data and update_data["project_id"] is not None:
            await self._ensure_project_exists(update_data["project_id"])

        for field, value in update_data.items():
            setattr(employee, field, value)

        try:
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise self._map_integrity_error(exc) from exc

        await self._db.refresh(employee)
        return EmployeeRead.model_validate(employee)

    async def delete_employee(self, employee_id: int) -> None:
        """Soft-delete an employee by setting employment_status to INACTIVE."""
        employee = await self._get_or_raise(employee_id)

        if employee.employment_status == EmploymentStatus.INACTIVE:
            return

        employee.employment_status = EmploymentStatus.INACTIVE

        try:
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise self._map_integrity_error(exc) from exc

    async def _get_or_raise(self, employee_id: int) -> Employee:
        result = await self._db.execute(
            select(Employee).where(Employee.id == employee_id),
        )
        employee = result.scalar_one_or_none()
        if employee is None:
            raise NotFoundError(f"Employee with id {employee_id} not found.")
        return employee

    async def _ensure_unique_email(
        self,
        email: str,
        *,
        exclude_id: int | None = None,
    ) -> None:
        query = select(Employee.id).where(Employee.email == email)
        if exclude_id is not None:
            query = query.where(Employee.id != exclude_id)

        existing_id = (await self._db.execute(query)).scalar_one_or_none()
        if existing_id is not None:
            raise ConflictError(f"Employee with email '{email}' already exists.")

    async def _ensure_unique_employee_code(
        self,
        employee_code: str,
        *,
        exclude_id: int | None = None,
    ) -> None:
        query = select(Employee.id).where(Employee.employee_code == employee_code)
        if exclude_id is not None:
            query = query.where(Employee.id != exclude_id)

        existing_id = (await self._db.execute(query)).scalar_one_or_none()
        if existing_id is not None:
            raise ConflictError(
                f"Employee with code '{employee_code}' already exists.",
            )

    async def _ensure_project_exists(self, project_id: int) -> None:
        result = await self._db.execute(
            select(Project.id).where(Project.id == project_id),
        )
        if result.scalar_one_or_none() is None:
            raise NotFoundError(f"Project with id {project_id} not found.")

    def _build_filter_conditions(self, filters: EmployeeListFilters) -> list:
        conditions: list = []

        if filters.status is None and not filters.include_inactive:
            conditions.append(Employee.employment_status != EmploymentStatus.INACTIVE)

        if filters.name:
            pattern = f"%{filters.name.strip()}%"
            conditions.append(
                or_(
                    Employee.first_name.ilike(pattern),
                    Employee.last_name.ilike(pattern),
                    func.concat(Employee.first_name, " ", Employee.last_name).ilike(
                        pattern,
                    ),
                ),
            )

        if filters.email:
            conditions.append(Employee.email.ilike(f"%{filters.email.strip()}%"))

        if filters.department:
            conditions.append(
                Employee.department.ilike(f"%{filters.department.strip()}%"),
            )

        if filters.status is not None:
            conditions.append(Employee.employment_status == filters.status)

        if filters.search:
            pattern = f"%{filters.search.strip()}%"
            conditions.append(
                or_(
                    Employee.employee_code.ilike(pattern),
                    Employee.email.ilike(pattern),
                    Employee.first_name.ilike(pattern),
                    Employee.last_name.ilike(pattern),
                    Employee.department.ilike(pattern),
                    Employee.job_title.ilike(pattern),
                    func.concat(Employee.first_name, " ", Employee.last_name).ilike(
                        pattern,
                    ),
                ),
            )

        return conditions

    @staticmethod
    def _map_integrity_error(exc: IntegrityError) -> ConflictError:
        message = str(exc.orig) if exc.orig else str(exc)
        lowered = message.lower()

        if "email" in lowered:
            return ConflictError("Employee with this email already exists.")
        if "employee_code" in lowered:
            return ConflictError("Employee with this employee code already exists.")
        if "project_id" in lowered or "projects" in lowered:
            return ConflictError("Referenced project does not exist.")

        return ConflictError("Operation conflicts with existing data.")

    @staticmethod
    def build_list_response(
        items: list[EmployeeRead],
        total: int,
        filters: EmployeeListFilters,
    ) -> dict:
        """Build a paginated response payload for the list endpoint."""
        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size,
            "total_pages": calculate_total_pages(total, filters.page_size),
        }
