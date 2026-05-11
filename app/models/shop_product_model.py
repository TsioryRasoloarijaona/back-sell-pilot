"""MongoDB shop product document models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ShopInfo(BaseModel):
    """Shop details stored with a product catalog."""

    name: str


class ProductItem(BaseModel):
    """Product details stored in a shop catalog."""

    name: str
    price: float
    description: str
    available: bool


class ShopProductDocument(BaseModel):
    """Internal representation of a user's shop products stored in MongoDB."""

    id: str | None = None
    user_id: str
    instagram_user_id: str
    shop: ShopInfo
    products: list[ProductItem]
    delivery: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mongo(cls, document: dict[str, Any]) -> "ShopProductDocument":
        """Convert a MongoDB document into a typed shop product document."""

        return cls(
            id=str(document["_id"]),
            user_id=document["user_id"],
            instagram_user_id=document["instagram_user_id"],
            shop=ShopInfo(**document["shop"]),
            products=[ProductItem(**product) for product in document.get("products", [])],
            delivery=document["delivery"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )


class ShopProductCreate(BaseModel):
    """Fields needed to create or replace a user's shop products."""

    shop: ShopInfo
    products: list[ProductItem]
    delivery: str
