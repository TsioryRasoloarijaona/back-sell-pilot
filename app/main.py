"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.config.settings import get_settings
from app.database.indexes import create_indexes
from app.dependencies import get_database, get_mongodb
from app.exceptions.custom_exceptions import AppException
from app.routers import auth_router, health_router, shop_product_router, user_router
from app.schemas.auth_schema import ErrorResponse
from app.utils.logger import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down application resources."""

    logger.info("Starting Instagram OAuth backend")
    try:
        create_indexes(get_database())
    except PyMongoError:
        logger.exception("MongoDB index creation failed")
        raise

    logger.info("MongoDB indexes are ready")
    try:
        yield
    finally:
        get_mongodb().close()
        logger.info("MongoDB connection closed")


app = FastAPI(
    title="Sellpilot Instagram OAuth API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """Convert custom application exceptions into JSON API errors."""

    logger.warning("%s: %s", exc.error_code, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.error_code, message=exc.message).model_dump(),
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return a safe response for unexpected failures."""

    logger.exception("Unhandled application error")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            message="Unexpected server error",
        ).model_dump(),
    )


app.include_router(health_router.router, prefix=settings.API_PREFIX)
app.include_router(auth_router.router, prefix=settings.API_PREFIX)
app.include_router(user_router.router, prefix=settings.API_PREFIX)
app.include_router(shop_product_router.router, prefix=settings.API_PREFIX)
