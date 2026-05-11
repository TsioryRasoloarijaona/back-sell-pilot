"""Shop product API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ShopInfoRequest(BaseModel):
    """Shop details accepted from the API."""

    name: str = Field(..., min_length=1)


class ProductItemRequest(BaseModel):
    """Product details accepted from the API."""

    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    description: str = Field(..., min_length=1)
    available: bool


class ShopProductsRequest(BaseModel):
    """Request body for registering a user's shop products."""

    shop: ShopInfoRequest
    products: list[ProductItemRequest] = Field(..., min_length=1)
    delivery: str = Field(..., min_length=1)


class ShopInfoResponse(BaseModel):
    """Shop details returned by the API."""

    name: str


class ProductItemResponse(BaseModel):
    """Product details returned by the API."""

    name: str
    price: float
    description: str
    available: bool


class ShopProductsResponse(BaseModel):
    """Stored shop products returned by the API."""

    id: str
    user_id: str
    instagram_user_id: str
    shop: ShopInfoResponse
    products: list[ProductItemResponse]
    delivery: str
    created_at: datetime
    updated_at: datetime
