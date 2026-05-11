"""MongoDB user repository."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.exceptions.custom_exceptions import DatabaseException
from app.models.user_model import UserCreate, UserDocument
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repository for user persistence."""

    def __init__(self, database: Database) -> None:
        self._collection: Collection = database["users"]

    def insert_user(self, user: UserCreate) -> UserDocument:
        """Insert a user and return the saved document."""

        now = datetime.now(timezone.utc)
        document: dict[str, Any] = {
            "instagram_user_id": user.instagram_user_id,
            "access_token": user.access_token,
            "token_type": user.token_type,
            "token_expires_in": user.token_expires_in,
            "token_created_at": user.token_created_at,
            "raw_token_response": user.raw_token_response,
            "created_at": now,
            "updated_at": now,
        }

        try:
            result = self._collection.insert_one(document)
            document["_id"] = result.inserted_id
            return UserDocument.from_mongo(document)
        except PyMongoError as error:
            logger.exception("MongoDB insert user failed")
            raise DatabaseException("Failed to insert user") from error

    def get_user_by_instagram_user_id(self, instagram_user_id: str) -> UserDocument | None:
        """Return a user by Instagram user id."""

        try:
            document = self._collection.find_one({"instagram_user_id": instagram_user_id})
            return UserDocument.from_mongo(document) if document else None
        except PyMongoError as error:
            logger.exception("MongoDB fetch by Instagram user id failed")
            raise DatabaseException("Failed to fetch user by Instagram user id") from error

    def get_user_by_id(self, user_id: str) -> UserDocument | None:
        """Return a user by internal MongoDB id."""

        try:
            object_id = ObjectId(user_id)
        except InvalidId:
            return None

        try:
            document = self._collection.find_one({"_id": object_id})
            return UserDocument.from_mongo(document) if document else None
        except PyMongoError as error:
            logger.exception("MongoDB fetch by internal user id failed")
            raise DatabaseException("Failed to fetch user by id") from error

    def update_token(
        self,
        instagram_user_id: str,
        access_token: str,
        token_type: str,
        token_expires_in: int | None,
        token_created_at: datetime,
        raw_token_response: dict[str, Any],
    ) -> UserDocument:
        """Update an existing user's Instagram token fields."""

        try:
            document = self._collection.find_one_and_update(
                {"instagram_user_id": instagram_user_id},
                {
                    "$set": {
                        "access_token": access_token,
                        "token_type": token_type,
                        "token_expires_in": token_expires_in,
                        "token_created_at": token_created_at,
                        "raw_token_response": raw_token_response,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as error:
            logger.exception("MongoDB update token failed")
            raise DatabaseException("Failed to update user token") from error

        if document is None:
            raise DatabaseException("User was not found while updating token")

        return UserDocument.from_mongo(document)
