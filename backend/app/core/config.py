"""Application settings and environment configuration."""

from functools import lru_cache
import ssl

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Environment-driven application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Ethara Seat Allocation & Project Mapping System"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://ethara:ethara_dev_password@localhost:5432/ethara_seat_allocation"
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 3600
    db_pool_timeout: int = 30
    db_echo: bool = False

    api_v1_prefix: str = "/api/v1"
    cors_origins: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins.",
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    log_level: str = "INFO"
    secret_key: str = "change-me-in-production"

    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    @property
    def sync_database_url(self) -> str:
        """Alembic requires a synchronous driver."""
        url = make_url(self.database_url)
        if url.drivername == "postgresql+asyncpg":
            url = url.set(drivername="postgresql")
        return url.render_as_string(hide_password=False)

    @property
    def async_database_url(self) -> str:
        """Return a clean asyncpg connection URL for SQLAlchemy async engine."""
        url = make_url(self.database_url)
        if url.drivername == "postgresql":
            url = url.set(drivername="postgresql+asyncpg")

        if url.drivername != "postgresql+asyncpg":
            return url.render_as_string(hide_password=False)
        query = dict(url.query)
        if "sslmode" in query or "channel_binding" in query:
            query.pop("sslmode", None)
            query.pop("channel_binding", None)
            url = url.set(query=query)

        return url.render_as_string(hide_password=False)

    @property
    def async_connect_args(self) -> dict[str, object]:
        """Translate common asyncpg connect arguments from the database URL."""
        url = make_url(self.database_url)
        if not url.drivername.startswith("postgresql"):
            return {}

        connect_args: dict[str, object] = {}
        sslmode = url.query.get("sslmode")
        if sslmode:
            connect_args["ssl"] = (
                False
                if sslmode == "disable"
                else ssl.create_default_context()
            )

        return connect_args

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def cors_methods_list(self) -> list[str]:
        if self.cors_allow_methods.strip() == "*":
            return ["*"]
        return [
            method.strip()
            for method in self.cors_allow_methods.split(",")
            if method.strip()
        ]

    @property
    def cors_headers_list(self) -> list[str]:
        if self.cors_allow_headers.strip() == "*":
            return ["*"]
        return [
            header.strip()
            for header in self.cors_allow_headers.split(",")
            if header.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
