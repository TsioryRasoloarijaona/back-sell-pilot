"""MongoDB index definitions."""

from pymongo import ASCENDING
from pymongo.database import Database


def create_indexes(database: Database) -> None:
    """Create all application indexes."""

    users = database["users"]
    users.create_index([("instagram_user_id", ASCENDING)], unique=True)
    users.create_index([("created_at", ASCENDING)])

    shop_products = database["shop_products"]
    shop_products.create_index([("user_id", ASCENDING)], unique=True)
    shop_products.create_index([("instagram_user_id", ASCENDING)])
