import secrets
from datetime import timedelta
from typing import Any, Callable, cast

import redis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.deps import require_access_token_payload
from app.core.redis_client import get_redis
from app.core.security import create_access_token

router = APIRouter()


@router.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"Connected to the API: {get_settings().app_name}"}


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "Healthy", "service": settings.app_name}


@router.get("/db-ping")
def db_ping(db: Session = Depends(get_db)) -> dict[str, bool | int]:
    one = cast(int, db.execute(text("SELECT 1")).scalar_one())
    return {"ok": True, "select_1": one}


@router.get("/redis-ping")
def redis_ping(r: redis.Redis = Depends(get_redis)):
    # Yes, even when using a shared pool, you use the dependency the same way.
    pong = cast(Callable[[], bool], r.ping)()
    return {"ok": True, "ping": pong}


@router.get("/app-testing/token-check")
def token_check(
    payload: dict = Depends(require_access_token_payload),
) -> dict[str, Any]:
    """Requires a valid access JWT (Authorization: Bearer). For manual / UI testing."""
    return {"valid": True, "user": payload.get("user")}


def _mint_app_testing_access_token(admin_code: str) -> dict[str, Any]:
    """Issue a short-lived JWT for local/manual API testing. Gated by env + shared secret."""
    settings = get_settings()
    if settings.environment not in ("development", "test"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="App testing token minting is only allowed in development or test",
        )
    expected = (settings.app_testing_admin_code or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="App testing token minting is disabled (set APP_TESTING_ADMIN_CODE)",
        )
    try:
        valid = len(admin_code) == len(expected) and secrets.compare_digest(
            admin_code, expected
        )
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin code",
        )
    # Synthetic user claim; not a DB row — use only for exercising JWT-protected routes.
    user_claims: dict[str, Any] = {
        "id": 0,
        "google_id": "app-testing-local",
        "email": "app-testing@local.invalid",
        "name": "App Testing",
        "picture": None,
        "id_number": None,
        "role_id": None,
        "flags": {"app_testing": True},
        "is_active": 1,
        "last_logged_in": None,
        "created_at": "1970-01-01T00:00:00Z",
        "updated_at": "1970-01-01T00:00:00Z",
        "deleted_at": None,
    }
    expires = timedelta(minutes=max(1, settings.app_testing_token_expire_minutes))
    access = create_access_token(user_claims, expires_delta=expires)
    return {
        "access_token": access,
        "token_type": "bearer",
        "expires_in_minutes": settings.app_testing_token_expire_minutes,
    }


@router.get("/app-testing/generate-token")
def generate_token(
    admin_code: str = Query(
        ...,
        alias="admin-code",
        description="Must match APP_TESTING_ADMIN_CODE (dev/test only).",
    ),
) -> dict[str, Any]:
    """Return a temporary access JWT for manual testing (`Authorization: Bearer ...`)."""
    return _mint_app_testing_access_token(admin_code)
