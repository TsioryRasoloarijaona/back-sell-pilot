"""Instagram OAuth integration service."""

from typing import Any
from urllib.parse import urlencode

import requests

from app.config.settings import Settings
from app.exceptions.custom_exceptions import OAuthException
from app.schemas.auth_schema import InstagramLongLivedToken, InstagramShortLivedToken
from app.utils.logger import get_logger

logger = get_logger(__name__)


class InstagramOAuthService:
    """Isolates all Instagram OAuth and token exchange behavior."""

    AUTHORIZATION_URL = "https://www.instagram.com/oauth/authorize"
    SHORT_LIVED_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
    LONG_LIVED_TOKEN_URL = "https://graph.instagram.com/access_token"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_authorization_url(self, state: str) -> str:
        """Build the Instagram OAuth authorization URL."""

        params = {
            "client_id": self._settings.APP_ID,
            "redirect_uri": self._settings.REDIRECT_URI,
            "response_type": "code",
            "scope": (
                "instagram_business_basic,"
                "instagram_business_manage_messages,"
                "instagram_business_manage_comments,"
                "instagram_business_content_publish"
            ),
            "state": state,
        }
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    def exchange_code_for_short_lived_token(self, code: str) -> InstagramShortLivedToken:
        """Exchange Instagram authorization code for a short-lived token."""

        payload = {
            "client_id": self._settings.APP_ID,
            "client_secret": self._settings.APP_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": self._settings.REDIRECT_URI,
            "code": code.split("#")[0].strip(),
        }

        try:
            response = requests.post(self.SHORT_LIVED_TOKEN_URL, data=payload, timeout=15)
            data: dict[str, Any] = response.json()
        except requests.RequestException as error:
            logger.exception("Instagram short-lived token exchange request failed")
            raise OAuthException("Instagram token exchange request failed") from error
        except ValueError as error:
            logger.exception("Instagram short-lived token response was not valid JSON")
            raise OAuthException("Instagram token exchange response was invalid") from error

        if response.status_code != 200:
            logger.error("Instagram short-lived token exchange failed: %s", data)
            raise OAuthException("Instagram token exchange failed")

        return InstagramShortLivedToken.model_validate(data)

    def exchange_short_lived_for_long_lived_token(
        self,
        short_lived_access_token: str,
    ) -> InstagramLongLivedToken:
        """Exchange a short-lived token for a long-lived Instagram token."""

        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": self._settings.APP_SECRET,
            "access_token": short_lived_access_token,
        }

        try:
            response = requests.get(self.LONG_LIVED_TOKEN_URL, params=params, timeout=15)
            data: dict[str, Any] = response.json()
        except requests.RequestException as error:
            logger.exception("Instagram long-lived token exchange request failed")
            raise OAuthException("Instagram long-lived token request failed") from error
        except ValueError as error:
            logger.exception("Instagram long-lived token response was not valid JSON")
            raise OAuthException("Instagram long-lived token response was invalid") from error

        if response.status_code != 200:
            logger.error("Instagram long-lived token exchange failed: %s", data)
            raise OAuthException("Instagram long-lived token exchange failed")

        return InstagramLongLivedToken.model_validate(data)
