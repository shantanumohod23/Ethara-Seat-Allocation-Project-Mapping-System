"""Project route handlers."""

from typing import Literal

from fastapi import APIRouter, Query, status

from app.api.deps import ProjectServiceDep
from app.models.enums import ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectEmployeeRead,
    ProjectListResponse,
    ProjectRead,
    ProjectUpdate,
)
from app.services.project_service import ProjectListFilters, ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse, summary="List projects")
async def list_projects(
    service: ProjectServiceDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: ProjectStatus | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
) -> ProjectListResponse:
    filters = ProjectListFilters(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        sort_order=sort_order,
    )
    items, total = await service.list_projects(filters)
    return ProjectListResponse(**ProjectService.build_list_response(items, total, filters))


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
async def create_project(payload: ProjectCreate, service: ProjectServiceDep) -> ProjectRead:
    return await service.create_project(payload)


@router.get("/{project_id}", response_model=ProjectRead, summary="Get project details")
async def get_project(project_id: int, service: ProjectServiceDep) -> ProjectRead:
    return await service.get_project(project_id)


@router.put("/{project_id}", response_model=ProjectRead, summary="Update project")
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    service: ProjectServiceDep,
) -> ProjectRead:
    return await service.update_project(project_id, payload)


@router.get(
    "/{project_id}/employees",
    response_model=list[ProjectEmployeeRead],
    summary="List employees in project",
)
async def list_project_employees(
    project_id: int,
    service: ProjectServiceDep,
) -> list[ProjectEmployeeRead]:
    return await service.list_project_employees(project_id)
