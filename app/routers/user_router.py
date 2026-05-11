"""User routes."""

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from app.schemas.auth_schema import AuthenticatedUser
from app.schemas.user_schema import UserResponse
from app.services.user_service import UserService
from app.dependencies import get_user_service
from app.exceptions.custom_exceptions import AuthenticationException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Return the authenticated user's public profile."""

    user = user_service.get_user_by_id(current_user.internal_user_id)
    if user is None or user.id is None:
        raise AuthenticationException("Authenticated user was not found")

    return UserResponse(
        id=user.id,
        instagram_user_id=user.instagram_user_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
