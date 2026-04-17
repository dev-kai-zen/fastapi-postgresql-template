from typing import Any
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.core.timezone import now_utc
from app.modules.auth.schema import TokenResponse
from app.modules.users.interface import UserPublic, default_users_port

_users_port = default_users_port()


def build_google_authorization_url(redirect_uri: str) -> str:
    settings = get_settings()
    if not settings.google_redirect_uri:
        raise ValueError("GOOGLE_REDIRECT_URI is not configured")
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "include_granted_scopes": "true",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def exchange_google_code(code: str, redirect_uri: str) -> dict[str, Any]:
    settings = get_settings()
    with httpx.Client(timeout=30.0) as client:
        token_res = client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_res.raise_for_status()
        access_token = token_res.json()["access_token"]
        user_res = client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_res.raise_for_status()
        return user_res.json()


def upsert_google_user(db: Session, profile: dict[str, Any]) -> UserPublic:
    sub = str(profile.get("sub") or "")
    if not sub:
        raise ValueError("Google profile missing sub")
    email = profile.get("email")
    if not email:
        raise ValueError("Google profile missing email")
    name = str(profile.get("name") or str(email).split("@", 1)[0])
    picture = profile.get("picture")
    if picture is not None and not isinstance(picture, str):
        picture = None
    elif picture == "":
        picture = None

    now = now_utc()
    return _users_port.upsert_google_identity(
        db,
        google_id=sub,
        email=email,
        name=name,
        picture=picture,
        last_logged_in=now,
    )


def issue_tokens_for_user(user_id: int) -> TokenResponse:
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return TokenResponse(access_token=access, refresh_token=refresh)
