"""Environment-driven application settings."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ID: str = Field(..., description="Instagram application/client id.")
    APP_SECRET: str = Field(..., description="Instagram application secret.")
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI.",
    )
    DATABASE_NAME: str = Field(default="sellpilot", description="MongoDB database name.")
    FRONTEND_URL: str = Field(..., description="React frontend origin.")
    FRONTEND_REDIRECT_PATH: str = Field(
        default="/dashboard",
        description="Frontend route to open after OAuth.",
    )
    COOKIE_NAME: str = Field(default="sellpilot_session", description="Auth cookie name.")
    COOKIE_SECRET: str = Field(..., description="Secret used to sign auth cookies.")
    REDIRECT_URI: str = Field(..., description="Instagram OAuth callback URL.")

    API_PREFIX: str = "/api"
    COOKIE_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 7
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        """Return allowed browser origins for credentialed React requests."""

        return [self.frontend_origin]

    @property
    def frontend_origin(self) -> str:
        """Return the frontend scheme, host, and port without any route path."""

        parsed_url = urlsplit(self.FRONTEND_URL.rstrip("/"))
        if parsed_url.scheme and parsed_url.netloc:
            return urlunsplit((parsed_url.scheme, parsed_url.netloc, "", "", ""))

        return self.FRONTEND_URL.rstrip("/")

    @property
    def frontend_redirect_url(self) -> str:
        """Return the full frontend URL used after successful OAuth."""

        redirect_path = self.FRONTEND_REDIRECT_PATH.strip()
        if not redirect_path or redirect_path == "/":
            return self.frontend_origin

        if not redirect_path.startswith("/"):
            redirect_path = f"/{redirect_path}"

        return f"{self.frontend_origin}{redirect_path}"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
