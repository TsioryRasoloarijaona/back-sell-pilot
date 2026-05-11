"""Authentication routes."""

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse

from app.config.settings import Settings, get_settings
from app.dependencies import get_auth_service, get_instagram_oauth_service
from app.middleware.auth_middleware import get_optional_current_user
from app.schemas.auth_schema import AuthMeResponse, AuthenticatedUser, LogoutResponse
from app.services.auth_service import AuthService
from app.services.instagram_oauth_service import InstagramOAuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
def login(
    settings: Settings = Depends(get_settings),
    auth_service: AuthService = Depends(get_auth_service),
    instagram_oauth_service: InstagramOAuthService = Depends(get_instagram_oauth_service),
) -> RedirectResponse:
    """Redirect the browser to Instagram OAuth."""

    oauth_state = auth_service.create_oauth_state()
    response = RedirectResponse(instagram_oauth_service.build_authorization_url(oauth_state))
    response.set_cookie(
        key=f"{settings.COOKIE_NAME}_oauth_state",
        value=oauth_state,
        max_age=600,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    return response


@router.get("/callback")
def callback(
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
    auth_service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """Handle Instagram OAuth callback, create a session cookie, and redirect frontend."""

    expected_state = request.cookies.get(f"{settings.COOKIE_NAME}_oauth_state")
    authenticated_user = auth_service.authenticate_with_instagram(code, state, expected_state)
    cookie_value = auth_service.create_session_cookie_value(authenticated_user.internal_user_id)

    response = RedirectResponse(settings.frontend_redirect_url)
    response.delete_cookie(
        key=f"{settings.COOKIE_NAME}_oauth_state",
        path="/",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
    )
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=cookie_value,
        max_age=settings.COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    return response


@router.post("/logout", response_model=LogoutResponse)
def logout(
    response: Response,
    settings: Settings = Depends(get_settings),
) -> LogoutResponse:
    """Clear the auth cookie."""

    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
    )
    return LogoutResponse()


@router.get("/me", response_model=AuthMeResponse)
def me(
    current_user: AuthenticatedUser | None = Depends(get_optional_current_user),
) -> AuthMeResponse:
    """Return the current authentication state for React."""

    if current_user is None:
        return AuthMeResponse(authenticated=False)

    return AuthMeResponse(
        authenticated=True,
        internal_user_id=current_user.internal_user_id,
        instagram_user_id=current_user.instagram_user_id,
    )
