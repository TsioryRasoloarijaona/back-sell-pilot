"""Custom exceptions converted to API responses in app startup."""


class AppException(Exception):
    """Base application exception."""

    status_code = 500
    error_code = "application_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class OAuthException(AppException):
    """Raised when Instagram OAuth fails."""

    status_code = 400
    error_code = "oauth_error"


class AuthenticationException(AppException):
    """Raised when cookie authentication fails."""

    status_code = 401
    error_code = "authentication_error"


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    status_code = 404
    error_code = "not_found"


class DatabaseException(AppException):
    """Raised when MongoDB operations fail."""

    status_code = 500
    error_code = "database_error"
