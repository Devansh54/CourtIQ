"""CourtIQ Exception Hierarchy.

Provides domain-specific exceptions for robust error handling across
configuration, networking, database persistence, and ETL transformations.
"""


class CourtIQError(Exception):
    """Base exception for all CourtIQ errors."""

    def __init__(self, message: str, details: dict = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(CourtIQError):
    """Raised when environment variables or application configuration are invalid."""
    pass


class APIError(CourtIQError):
    """Base exception for external API integration failures."""

    def __init__(self, message: str, status_code: int = None, details: dict = None) -> None:
        super().__init__(message, details)
        self.status_code = status_code


class RateLimitError(APIError):
    """Raised when the Sportradar API returns 429 Too Many Requests."""

    def __init__(self, message: str = "Sportradar API rate limit exceeded (429)", retry_after: float = None) -> None:
        super().__init__(message, status_code=429, details={"retry_after": retry_after})
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Raised when Sportradar credentials are unauthorized or forbidden (401/403)."""

    def __init__(self, message: str = "Sportradar API authentication failed (401/403)") -> None:
        super().__init__(message, status_code=401)


class ResourceNotFoundError(APIError):
    """Raised when an API endpoint or resource is not found (404)."""

    def __init__(self, endpoint: str) -> None:
        super().__init__(f"Resource not found at endpoint: {endpoint}", status_code=404)


class DatabaseError(CourtIQError):
    """Base exception for relational database operations."""
    pass


class MigrationError(DatabaseError):
    """Raised when a DDL migration fails to execute."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a requested entity does not exist in the database."""
    pass


class DataValidationError(CourtIQError):
    """Raised when ingested data violates schema contracts or constraints."""
    pass


class TransformationError(CourtIQError):
    """Raised when an extractor or transformer fails to parse raw payload structures."""
    pass
