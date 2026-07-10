"""Version 1 API router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import ai, dashboard, employees, projects, seat_allocations, seats

api_router = APIRouter()

api_router.include_router(employees.router)
api_router.include_router(projects.router)
api_router.include_router(seat_allocations.router)
api_router.include_router(seats.router)
api_router.include_router(dashboard.router)
api_router.include_router(ai.router)
