"""MongoDB user document models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserDocument(BaseModel):
    """Internal representation of a user stored in MongoDB."""

    id: str | None = Field(default=None)
    instagram_user_id: str
    access_token: str
    token_type: str = "long_lived"
    token_expires_in: int | None = None
    token_created_at: datetime
    raw_token_response: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mongo(cls, document: dict[str, Any]) -> "UserDocument":
        """Convert a MongoDB document into a typed user document."""

        return cls(
            id=str(document["_id"]),
            instagram_user_id=document["instagram_user_id"],
            access_token=document["access_token"],
            token_type=document.get("token_type", "long_lived"),
            token_expires_in=document.get("token_expires_in"),
            token_created_at=document["token_created_at"],
            raw_token_response=document.get("raw_token_response", {}),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )


class UserCreate(BaseModel):
    """Fields needed to create a MongoDB user document."""

    instagram_user_id: str
    access_token: str
    token_type: str = "long_lived"
    token_expires_in: int | None = None
    token_created_at: datetime
    raw_token_response: dict[str, Any]
