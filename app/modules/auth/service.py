from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token
from app.modules.auth.google_oauth_client import GoogleOAuthClient, OAuthClientError
from app.modules.auth.users_client import UsersClient
from app.modules.users.schema import UserGoogleInfo

_google_oauth_client = GoogleOAuthClient()
_users_client = UsersClient()


def get_google_login_redirect_url() -> str:
    return _google_oauth_client.build_authorization_url()


async def complete_google_oauth(db: Session, code: str) -> str:
    try:
        tokens = await _google_oauth_client.exchange_code_for_tokens(code)
        raw_profile = await _google_oauth_client.get_user_info(
            tokens["access_token"]
        )
    except OAuthClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    google_user = UserGoogleInfo.model_validate(raw_profile)
    user_public = _users_client.upsert_google_identity(db, google_user)
    jwt_token = create_access_token(user_public.model_dump(mode="json"))
    settings = get_settings()
    return f"{settings.frontend_oauth_success_url}#access_token={jwt_token}"
