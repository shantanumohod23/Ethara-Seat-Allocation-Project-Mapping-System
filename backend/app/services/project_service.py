"""Project domain service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.employee import Employee
from app.models.enums import ProjectStatus
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectEmployeeRead,
    ProjectRead,
    ProjectUpdate,
)
from app.utils.pagination import calculate_offset, calculate_total_pages


@dataclass(frozen=True, slots=True)
class ProjectListFilters:
    """Query parameters for listing projects."""

    page: int = 1
    page_size: int = 20
    search: str | None = None
    status: ProjectStatus | None = None
    sort_order: Literal["asc", "desc"] = "asc"


class ProjectService:
    """Business logic for project CRUD and membership lookup."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_projects(self, filters: ProjectListFilters) -> tuple[list[ProjectRead], int]:
        query = select(Project)
        count_query = select(func.count()).select_from(Project)
        conditions = []
        if filters.search:
            pattern = f"%{filters.search.strip()}%"
            conditions.append(
                or_(
                    Project.project_code.ilike(pattern),
                    Project.name.ilike(pattern),
                    Project.manager_name.ilike(pattern),
                ),
            )
        if filters.status is not None:
            conditions.append(Project.status == filters.status)
        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)

        order = Project.name.desc() if filters.sort_order == "desc" else Project.name.asc()
        query = query.order_by(order, Project.id.asc()).offset(
            calculate_offset(filters.page, filters.page_size),
        ).limit(filters.page_size)

        total = (await self._db.execute(count_query)).scalar_one()
        projects = (await self._db.execute(query)).scalars().all()
        return [ProjectRead.model_validate(project) for project in projects], total

    async def get_project(self, project_id: int) -> ProjectRead:
        return ProjectRead.model_validate(await self._get_or_raise(project_id))

    async def create_project(self, data: ProjectCreate) -> ProjectRead:
        project = Project(**data.model_dump())
        self._db.add(project)
        try:
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise ConflictError("Project code already exists.") from exc
        await self._db.refresh(project)
        return ProjectRead.model_validate(project)

    async def update_project(self, project_id: int, data: ProjectUpdate) -> ProjectRead:
        project = await self._get_or_raise(project_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        try:
            await self._db.commit()
        except IntegrityError as exc:
            await self._db.rollback()
            raise ConflictError("Project update conflicts with existing data.") from exc
        await self._db.refresh(project)
        return ProjectRead.model_validate(project)

    async def list_project_employees(self, project_id: int) -> list[ProjectEmployeeRead]:
        await self._get_or_raise(project_id)
        result = await self._db.execute(
            select(Employee)
            .where(Employee.project_id == project_id)
            .order_by(Employee.last_name.asc(), Employee.first_name.asc()),
        )
        return [
            ProjectEmployeeRead(
                id=employee.id,
                employee_code=employee.employee_code,
                name=f"{employee.first_name} {employee.last_name}",
                email=employee.email,
                department=employee.department,
                employment_status=employee.employment_status.value,
            )
            for employee in result.scalars().all()
        ]

    async def _get_or_raise(self, project_id: int) -> Project:
        project = (
            await self._db.execute(select(Project).where(Project.id == project_id))
        ).scalar_one_or_none()
        if project is None:
            raise NotFoundError(f"Project with id {project_id} not found.")
        return project

    @staticmethod
    def build_list_response(
        items: list[ProjectRead],
        total: int,
        filters: ProjectListFilters,
    ) -> dict:
        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size,
            "total_pages": calculate_total_pages(total, filters.page_size),
        }
