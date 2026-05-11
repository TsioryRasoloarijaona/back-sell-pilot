"""User business logic."""

from datetime import datetime, timezone

from app.models.user_model import UserCreate, UserDocument
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import InstagramLongLivedToken
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Coordinates user creation and token updates."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def get_user_by_id(self, user_id: str) -> UserDocument | None:
        """Return a user by internal id."""

        return self._user_repository.get_user_by_id(user_id)

    def find_or_create_from_instagram_token(
        self,
        instagram_user_id: str,
        token: InstagramLongLivedToken,
    ) -> UserDocument:
        """Create a user or update its server-side Instagram token."""

        existing_user = self._user_repository.get_user_by_instagram_user_id(instagram_user_id)
        token_created_at = datetime.now(timezone.utc)
        token_type = token.token_type or "long_lived"
        raw_token_response = token.model_dump()

        if existing_user is None:
            user = self._user_repository.insert_user(
                UserCreate(
                    instagram_user_id=instagram_user_id,
                    access_token=token.access_token,
                    token_type=token_type,
                    token_expires_in=token.expires_in,
                    token_created_at=token_created_at,
                    raw_token_response=raw_token_response,
                )
            )
            logger.info("Created Instagram user %s as internal user %s", instagram_user_id, user.id)
            return user

        user = self._user_repository.update_token(
            instagram_user_id=instagram_user_id,
            access_token=token.access_token,
            token_type=token_type,
            token_expires_in=token.expires_in,
            token_created_at=token_created_at,
            raw_token_response=raw_token_response,
        )
        logger.info("Updated Instagram token for internal user %s", user.id)
        return user
