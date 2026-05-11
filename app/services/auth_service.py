"""Authentication orchestration service."""

from app.config.settings import Settings
from app.exceptions.custom_exceptions import AuthenticationException, OAuthException
from app.schemas.auth_schema import AuthenticatedUser
from app.services.instagram_oauth_service import InstagramOAuthService
from app.services.user_service import UserService
from app.utils.logger import get_logger
from app.utils.security import generate_oauth_state, sign_user_id, verify_signed_user_id

logger = get_logger(__name__)


class AuthService:
    """Coordinates Instagram OAuth, user persistence, and cookie auth."""

    def __init__(
        self,
        settings: Settings,
        instagram_oauth_service: InstagramOAuthService,
        user_service: UserService,
    ) -> None:
        self._settings = settings
        self._instagram_oauth_service = instagram_oauth_service
        self._user_service = user_service

    def create_oauth_state(self) -> str:
        """Create a random OAuth state value."""

        return generate_oauth_state()

    def authenticate_with_instagram(
        self,
        code: str | None,
        state: str | None,
        expected_state: str | None,
    ) -> AuthenticatedUser:
        """Complete Instagram OAuth and return authenticated user details."""

        if not code:
            logger.warning("Instagram OAuth callback was missing code")
            raise OAuthException("Instagram authorization failed")

        if not state or not expected_state or state != expected_state:
            logger.warning("Instagram OAuth state validation failed")
            raise OAuthException("Instagram authorization state was invalid")

        short_lived_token = self._instagram_oauth_service.exchange_code_for_short_lived_token(code)
        long_lived_token = self._instagram_oauth_service.exchange_short_lived_for_long_lived_token(
            short_lived_token.access_token
        )
        user = self._user_service.find_or_create_from_instagram_token(
            instagram_user_id=str(short_lived_token.user_id),
            token=long_lived_token,
        )

        if user.id is None:
            raise AuthenticationException("Authenticated user id was not available")

        logger.info("Successful Instagram login for internal user %s", user.id)
        return AuthenticatedUser(
            internal_user_id=user.id,
            instagram_user_id=user.instagram_user_id,
        )

    def create_session_cookie_value(self, internal_user_id: str) -> str:
        """Create a signed cookie value containing only the internal user id."""

        return sign_user_id(internal_user_id, self._settings.COOKIE_SECRET)

    def get_authenticated_user(self, cookie_value: str | None) -> AuthenticatedUser:
        """Resolve a signed cookie to an authenticated user."""

        if not cookie_value:
            raise AuthenticationException("Authentication cookie is missing")

        internal_user_id = verify_signed_user_id(cookie_value, self._settings.COOKIE_SECRET)
        if internal_user_id is None:
            raise AuthenticationException("Authentication cookie is invalid")

        user = self._user_service.get_user_by_id(internal_user_id)
        if user is None or user.id is None:
            raise AuthenticationException("Authenticated user was not found")

        return AuthenticatedUser(
            internal_user_id=user.id,
            instagram_user_id=user.instagram_user_id,
        )
