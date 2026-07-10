"""Health check route handlers."""

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.db.health import verify_database_connection
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application health check",
    responses={
        status.HTTP_200_OK: {"description": "Application is healthy."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Application is unhealthy."},
    },
)
async def health_check(response: Response) -> HealthResponse:
    """Return application and database health status."""
    try:
        await verify_database_connection()
        return HealthResponse(
            status="healthy",
            database="connected",
            version=settings.app_version,
        )
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(
            status="unhealthy",
            database="disconnected",
            version=settings.app_version,
        )
