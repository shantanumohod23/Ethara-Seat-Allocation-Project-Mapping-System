"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.lifespan import lifespan


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for Ethara seat allocation and project mapping.",
        lifespan=lifespan,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        debug=settings.debug,
    )
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "application": "Ethara Seat Allocation & Project Mapping System",
            "status": "running",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
            "openapi": "/openapi.json"
        }
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_headers_list,
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
