"""Shop product routes."""

from fastapi import APIRouter, Depends

from app.dependencies import get_shop_product_service
from app.exceptions.custom_exceptions import NotFoundException
from app.middleware.auth_middleware import get_current_user
from app.models.shop_product_model import ShopProductDocument
from app.schemas.auth_schema import AuthenticatedUser
from app.schemas.shop_product_schema import ShopProductsRequest, ShopProductsResponse
from app.services.shop_product_service import ShopProductService

router = APIRouter(prefix="/shop", tags=["shop"])


def _to_response(shop_products: ShopProductDocument) -> ShopProductsResponse:
    """Convert a shop product document to an API response."""

    return ShopProductsResponse(
        id=shop_products.id or "",
        user_id=shop_products.user_id,
        instagram_user_id=shop_products.instagram_user_id,
        shop=shop_products.shop.model_dump(),
        products=[product.model_dump() for product in shop_products.products],
        delivery=shop_products.delivery,
        created_at=shop_products.created_at,
        updated_at=shop_products.updated_at,
    )


@router.post("/products", response_model=ShopProductsResponse)
def register_shop_products(
    payload: ShopProductsRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    shop_product_service: ShopProductService = Depends(get_shop_product_service),
) -> ShopProductsResponse:
    """Create or replace the authenticated user's shop products."""

    shop_products = shop_product_service.register_shop_products(current_user, payload)
    return _to_response(shop_products)


@router.get("/products", response_model=ShopProductsResponse)
def get_shop_products(
    current_user: AuthenticatedUser = Depends(get_current_user),
    shop_product_service: ShopProductService = Depends(get_shop_product_service),
) -> ShopProductsResponse:
    """Return the authenticated user's shop products."""

    shop_products = shop_product_service.get_shop_products(current_user)
    if shop_products is None:
        raise NotFoundException("Shop products were not found")

    return _to_response(shop_products)
