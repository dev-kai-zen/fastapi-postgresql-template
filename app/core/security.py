from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import Settings, get_settings

import bcrypt

import jwt


def create_access_token(
    user: dict,
    roles: list[dict],
    permissions: list[dict] = [],
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Return a signed JWT access token. `subject` is stored as the `sub` claim."""
    settings: Settings = get_settings()
    now = datetime.now(UTC)
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = now + expires_delta
    payload: dict[str, Any] = {
        "user": user,
        "roles": roles,
        "permissions": permissions,
        "exp": expire,
        "iat": now,
    }
    if extra_claims:
        payload.update(extra_claims)
    secret_key: str = settings.jwt_secret_key
    algorithm: str = settings.jwt_algorithm
    return jwt.encode(payload, secret_key, algorithm=algorithm)  # type: ignore


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate and decode a JWT. Raises `jwt.PyJWTError` subclasses if invalid or expired."""
    settings: Settings = get_settings()
    secret_key: str = settings.jwt_secret_key
    algorithm: str = settings.jwt_algorithm

    # type: ignore
    return jwt.decode(token, secret_key, algorithms=[algorithm])


# bcrypt truncates secrets longer than 72 bytes; keep passwords within normal UX limits.
_MAX_PASSWORD_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage (bcrypt). Returns an ASCII string safe for UTF-8 text columns."""
    secret = plain_password.encode("utf-8")
    if len(secret) > _MAX_PASSWORD_BYTES:
        secret = secret[:_MAX_PASSWORD_BYTES]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(secret, salt)
    return hashed.decode("ascii")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if `plain_password` matches the bcrypt `password_hash` string."""
    secret = plain_password.encode("utf-8")
    if len(secret) > _MAX_PASSWORD_BYTES:
        secret = secret[:_MAX_PASSWORD_BYTES]
    try:
        return bcrypt.checkpw(secret, password_hash.encode("ascii"))
    except ValueError:
        return False
