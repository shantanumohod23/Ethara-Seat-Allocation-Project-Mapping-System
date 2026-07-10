"""Database connectivity helpers."""

from sqlalchemy import text

from app.core.exceptions import DatabaseUnavailableError
from app.db.session import engine


async def verify_database_connection() -> None:
    """
    Verify PostgreSQL is reachable.

    Raises:
        DatabaseUnavailableError: If the database cannot be reached.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise DatabaseUnavailableError(
            "Unable to establish a connection with PostgreSQL."
        ) from exc
