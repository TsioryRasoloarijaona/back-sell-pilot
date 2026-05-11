"""MongoDB shop product repository."""

from datetime import datetime, timezone
from typing import Any

from pymongo import ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.exceptions.custom_exceptions import DatabaseException
from app.models.shop_product_model import ShopProductCreate, ShopProductDocument
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ShopProductRepository:
    """Repository for user shop product persistence."""

    def __init__(self, database: Database) -> None:
        self._collection: Collection = database["shop_products"]

    def upsert_for_user(
        self,
        user_id: str,
        instagram_user_id: str,
        shop_products: ShopProductCreate,
    ) -> ShopProductDocument:
        """Create or replace the authenticated user's shop products."""

        now = datetime.now(timezone.utc)
        document: dict[str, Any] = {
            "user_id": user_id,
            "instagram_user_id": instagram_user_id,
            "shop": shop_products.shop.model_dump(),
            "products": [product.model_dump() for product in shop_products.products],
            "delivery": shop_products.delivery,
            "updated_at": now,
        }

        try:
            saved_document = self._collection.find_one_and_update(
                {"user_id": user_id},
                {
                    "$set": document,
                    "$setOnInsert": {"created_at": now},
                },
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as error:
            logger.exception("MongoDB upsert shop products failed")
            raise DatabaseException("Failed to save shop products") from error

        if saved_document is None:
            raise DatabaseException("Shop products were not saved")

        return ShopProductDocument.from_mongo(saved_document)

    def get_for_user(self, user_id: str) -> ShopProductDocument | None:
        """Return the authenticated user's shop products."""

        try:
            document = self._collection.find_one({"user_id": user_id})
            return ShopProductDocument.from_mongo(document) if document else None
        except PyMongoError as error:
            logger.exception("MongoDB fetch shop products failed")
            raise DatabaseException("Failed to fetch shop products") from error
