import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import create_access_token
from app.core.refresh_token import service as refresh_token_service
from app.modules.auth.oauth_client import GoogleOAuthClient, OAuthClientError
from app.modules.auth.users_client import UsersClient

_oauth_client = GoogleOAuthClient()
_users_client = UsersClient()


def _mint_access_token_for_user(user_id: int) -> dict:
    access_token = create_access_token(user_id)
    return {"access_token": access_token}


def get_google_login_redirect_url() -> str:
    return _oauth_client.build_authorization_url()


async def complete_google_oauth(code: str) -> dict:
    try:
        tokens = await _oauth_client.exchange_code_for_tokens(code)
        raw_profile = await _oauth_client.get_user_info(tokens["access_token"])
    except OAuthClientError as exc:
        raise HTTPException(status_code=exc.status_code,
                            detail=exc.detail) from exc

    db: Session = SessionLocal()
    try:
        user_read = _users_client.upsert_google_identity(db, raw_profile)
        access_token_result = _mint_access_token_for_user(user_read.id)
        refresh = refresh_token_service.issue_refresh_token(db, user_read.id)
        return {
            "access_token": access_token_result["access_token"],
            "refresh_token": refresh,
        }
    finally:
        db.close()


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """Validate refresh session, then mint access JWT via users + RBAC clients."""
    try:
        payload = refresh_token_service.verify_refresh_session(
            db, refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc
    sub = payload.get("sub")
    try:
        user_id = int(sub) if sub is not None else -1
    except (TypeError, ValueError):
        user_id = -1
    if user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token; sign in again",
        )
    try:
        user_read = _users_client.get_user_by_id(db, user_id)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token; sign in again",
            ) from exc
        raise
    return _mint_access_token_for_user(user_read.id)


def refresh_access_from_cookie(db: Session, refresh_token: str | None) -> dict:
    """Mint a new access token from the refresh cookie; raises HTTPException if missing/invalid."""
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    return refresh_access_token(db, refresh_token)


def logout_revoking_refresh_token(db: Session, refresh_token: str | None) -> None:
    """Revoke refresh JWT in the database; ignores errors so logout always clears cookie."""
    if not refresh_token:
        return
    try:
        refresh_token_service.revoke_refresh_token(db, refresh_token)
    except Exception:
        pass
