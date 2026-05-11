"""Cookie signing and verification helpers."""

import base64
import hashlib
import hmac
import secrets


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def sign_user_id(user_id: str, secret: str) -> str:
    """Return a signed cookie payload containing only the internal user id."""

    encoded_user_id = _encode(user_id.encode("utf-8"))
    signature = hmac.new(
        secret.encode("utf-8"),
        encoded_user_id.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_user_id}.{_encode(signature)}"


def verify_signed_user_id(cookie_value: str, secret: str) -> str | None:
    """Validate a signed cookie and return the internal user id."""

    try:
        encoded_user_id, encoded_signature = cookie_value.split(".", 1)
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            encoded_user_id.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        actual_signature = _decode(encoded_signature)
    except (ValueError, TypeError):
        return None

    if not hmac.compare_digest(expected_signature, actual_signature):
        return None

    try:
        return _decode(encoded_user_id).decode("utf-8")
    except UnicodeDecodeError:
        return None


def generate_oauth_state() -> str:
    """Return a cryptographically random OAuth state value."""

    return secrets.token_urlsafe(32)
