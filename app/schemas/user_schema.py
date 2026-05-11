"""User API schemas."""

from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Public user response. Never exposes Instagram access tokens."""

    id: str
    instagram_user_id: str
    created_at: datetime
    updated_at: datetime
