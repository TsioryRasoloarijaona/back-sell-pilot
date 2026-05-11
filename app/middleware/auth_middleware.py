"""Centralized cookie authentication dependency."""

from fastapi import Depends, Request

from app.config.settings import Settings, get_settings
from app.dependencies import get_auth_service
from app.exceptions.custom_exceptions import AuthenticationException
from app.schemas.auth_schema import AuthenticatedUser
from app.services.auth_service import AuthService


def get_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUser:
    """Validate the signed auth cookie and return the current user."""

    cookie_value = request.cookies.get(settings.COOKIE_NAME)
    return auth_service.get_authenticated_user(cookie_value)


def get_optional_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUser | None:
    """Return the current user when authenticated, otherwise None."""

    try:
        cookie_value = request.cookies.get(settings.COOKIE_NAME)
        return auth_service.get_authenticated_user(cookie_value)
    except AuthenticationException:
        return None
