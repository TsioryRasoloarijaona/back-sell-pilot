"""Authentication request and response schemas."""

from pydantic import BaseModel


class InstagramShortLivedToken(BaseModel):
    """Instagram short-lived OAuth token response."""

    access_token: str
    user_id: int | str


class InstagramLongLivedToken(BaseModel):
    """Instagram long-lived token response."""

    access_token: str
    token_type: str | None = None
    expires_in: int | None = None


class AuthenticatedUser(BaseModel):
    """Authenticated user details used by auth endpoints."""

    internal_user_id: str
    instagram_user_id: str


class AuthMeResponse(BaseModel):
    """Response returned by /api/auth/me."""

    authenticated: bool
    internal_user_id: str | None = None
    instagram_user_id: str | None = None


class LogoutResponse(BaseModel):
    """Logout response."""

    authenticated: bool = False
    message: str = "Logged out"


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
