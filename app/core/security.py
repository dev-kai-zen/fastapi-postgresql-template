from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import Settings, get_settings

from contextlib import contextmanager
from collections.abc import Generator
import uuid

import redis

import bcrypt

import jwt


def create_access_token(
    user: dict,
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
    
    return jwt.decode(token, secret_key, algorithms=[algorithm]) # type: ignore


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


_REFRESH_REVOKE_PREFIX = "auth:refresh:revoked:"


@contextmanager
def _redis_client() -> Generator[redis.Redis, None, None]:
    client = redis.from_url(get_settings().redis_url, decode_responses=True)
    try:
        yield client
    finally:
        client.close()


def _decode_refresh_payload(token: str) -> dict[str, Any]:
    """Verify signature and expiry; ensure claims mark this as a refresh token."""
    settings: Settings = get_settings()
    secret_key: str = settings.jwt_secret_key
    algorithm: str = settings.jwt_algorithm
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])  # type: ignore
    if payload.get("token_use") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    jti = payload.get("jti")
    if not jti or not isinstance(jti, str):
        raise jwt.InvalidTokenError("Refresh token missing jti")
    return payload


def create_refresh_token(
    subject: str | int,
    *,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Return a signed refresh JWT (`token_use=refresh`, unique `jti`)."""
    settings: Settings = get_settings()
    now = datetime.now(UTC)
    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expire = now + expires_delta
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "token_use": "refresh",
    }
    if extra_claims:
        payload.update(extra_claims)
    secret_key: str = settings.jwt_secret_key
    algorithm: str = settings.jwt_algorithm
    return jwt.encode(payload, secret_key, algorithm=algorithm)  # type: ignore


def verify_refresh_token(token: str) -> dict[str, Any]:
    """Decode a refresh token and ensure it has not been revoked (Redis)."""
    payload = _decode_refresh_payload(token)
    jti = str(payload["jti"])
    with _redis_client() as r:
        if r.get(f"{_REFRESH_REVOKE_PREFIX}{jti}"):
            raise jwt.InvalidTokenError("Refresh token has been revoked")
    return payload


def revoke_refresh_token(token: str) -> None:
    """Store `jti` in Redis until token expiry so `verify_refresh_token` rejects it. Idempotent."""
    payload = _decode_refresh_payload(token)
    jti = str(payload["jti"])
    exp = payload.get("exp")
    if exp is None:
        return
    exp_ts = int(exp)
    remaining = exp_ts - int(datetime.now(UTC).timestamp())
    if remaining <= 0:
        return
    with _redis_client() as r:
        r.setex(f"{_REFRESH_REVOKE_PREFIX}{jti}", remaining, "1")
