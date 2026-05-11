"""Application dependency providers."""

from functools import lru_cache

from pymongo.database import Database

from app.config.settings import get_settings
from app.database.mongodb import MongoDB
from app.repositories.shop_product_repository import ShopProductRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.instagram_oauth_service import InstagramOAuthService
from app.services.shop_product_service import ShopProductService
from app.services.user_service import UserService


@lru_cache
def get_mongodb() -> MongoDB:
    """Return the shared MongoDB connection manager."""

    settings = get_settings()
    return MongoDB(settings.MONGODB_URI, settings.DATABASE_NAME)


def get_database() -> Database:
    """Return the configured MongoDB database."""

    return get_mongodb().database


def get_user_repository() -> UserRepository:
    """Return the user repository."""

    return UserRepository(get_database())


def get_shop_product_repository() -> ShopProductRepository:
    """Return the shop product repository."""

    return ShopProductRepository(get_database())


def get_instagram_oauth_service() -> InstagramOAuthService:
    """Return the Instagram OAuth service."""

    return InstagramOAuthService(get_settings())


def get_user_service() -> UserService:
    """Return the user service."""

    return UserService(get_user_repository())


def get_shop_product_service() -> ShopProductService:
    """Return the shop product service."""

    return ShopProductService(get_shop_product_repository())


def get_auth_service() -> AuthService:
    """Return the auth service."""

    return AuthService(
        settings=get_settings(),
        instagram_oauth_service=get_instagram_oauth_service(),
        user_service=get_user_service(),
    )
