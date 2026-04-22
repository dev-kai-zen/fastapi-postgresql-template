from datetime import UTC, datetime, timedelta
from typing import Any
import uuid

import jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.refresh_token import repository as refresh_token_repository

from app.core.timezone import now_app


def _decode_refresh_payload(token: str) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(  # type: ignore[no-untyped-call]
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    if payload.get("token_use") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    jti = payload.get("jti")
    if not jti or not isinstance(jti, str):
        raise jwt.InvalidTokenError("Refresh token missing jti")
    return payload


def verify_refresh_session(db: Session, token: str) -> dict[str, Any]:
    payload = _decode_refresh_payload(token)
    jti = str(payload["jti"])
    row = refresh_token_repository.get_active_by_jti(db, jti)
    if row is None:
        raise jwt.InvalidTokenError("Refresh token revoked or unknown")
    return payload


def issue_refresh_token(
    db: Session,
    subject: str | int,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    now = now_app()
    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expire = now + expires_delta
    jti = str(uuid.uuid4())
    refresh_token_repository.insert_token(
        db, jti=jti, user_id=int(subject), expires_at=expire)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "jti": jti,
        "token_use": "refresh",
    }
    return jwt.encode(  # type: ignore[no-untyped-call]
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def revoke_refresh_token(db: Session, token: str) -> None:
    try:
        payload = _decode_refresh_payload(token)
    except jwt.PyJWTError:
        return
    refresh_token_repository.revoke_by_jti(db, str(payload["jti"]))
