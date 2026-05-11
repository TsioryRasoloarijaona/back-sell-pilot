"""Shop product business logic."""

from app.models.shop_product_model import (
    ProductItem,
    ShopInfo,
    ShopProductCreate,
    ShopProductDocument,
)
from app.repositories.shop_product_repository import ShopProductRepository
from app.schemas.auth_schema import AuthenticatedUser
from app.schemas.shop_product_schema import ShopProductsRequest


class ShopProductService:
    """Coordinates shop product creation and retrieval."""

    def __init__(self, shop_product_repository: ShopProductRepository) -> None:
        self._shop_product_repository = shop_product_repository

    def register_shop_products(
        self,
        current_user: AuthenticatedUser,
        payload: ShopProductsRequest,
    ) -> ShopProductDocument:
        """Create or replace shop products for the authenticated user."""

        shop_products = ShopProductCreate(
            shop=ShopInfo(name=payload.shop.name),
            products=[
                ProductItem(
                    name=product.name,
                    price=product.price,
                    description=product.description,
                    available=product.available,
                )
                for product in payload.products
            ],
            delivery=payload.delivery,
        )

        return self._shop_product_repository.upsert_for_user(
            user_id=current_user.internal_user_id,
            instagram_user_id=current_user.instagram_user_id,
            shop_products=shop_products,
        )

    def get_shop_products(self, current_user: AuthenticatedUser) -> ShopProductDocument | None:
        """Return shop products for the authenticated user."""

        return self._shop_product_repository.get_for_user(current_user.internal_user_id)
