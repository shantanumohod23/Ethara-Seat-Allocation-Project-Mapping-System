"""Application lifespan events."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import DatabaseUnavailableError
from app.core.logging import get_logger, setup_logging
from app.db.health import verify_database_connection
from app.db.session import close_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown lifecycle events."""
    setup_logging()
    logger.info("Starting %s v%s [%s]", settings.app_name, settings.app_version, settings.environment)

    try:
        await verify_database_connection()
        logger.info("PostgreSQL connection verified successfully.")
    except DatabaseUnavailableError:
        logger.exception("Failed to connect to PostgreSQL on startup.")
        raise

    yield

    logger.info("Shutting down application.")
    await close_db()
    logger.info("Database connection pool disposed.")
