"""Application-specific exception types."""


class AppException(Exception):
    """Base class for domain and application errors."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(message, status_code=404)


class ConflictError(AppException):
    """Raised when a request conflicts with existing data."""

    def __init__(self, message: str = "Resource conflict.") -> None:
        super().__init__(message, status_code=409)


class DatabaseUnavailableError(AppException):
    """Raised when the database cannot be reached."""

    def __init__(self, message: str = "Database is unavailable.") -> None:
        super().__init__(message, status_code=503)
