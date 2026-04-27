import jwt
from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.constants import NEW_ACCESS_TOKEN_HEADER, REFRESH_TOKEN_COOKIE_NAME
from app.core.db import get_db
from app.core.security import decode_access_token

from app.dependencies.auth_client import AuthClient

_auth_client = AuthClient()
_bearer = HTTPBearer(auto_error=False)


def require_access_token_payload(
    response: Response,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
) -> dict:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    access = creds.credentials
    try:
        return decode_access_token(access)
    except jwt.ExpiredSignatureError:
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired; sign in again",
            )
        new_access = _auth_client.refresh_access_token()
        response.headers[NEW_ACCESS_TOKEN_HEADER] = new_access["access_token"]
        return decode_access_token(new_access["access_token"])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )


def require_current_user_id(
    payload: dict = Depends(require_access_token_payload),
) -> int:
    """Numeric `users.id` from  the access token `sub` claim."""
    sub = payload.get("sub")
    try:
        uid = int(sub) if sub is not None else -1
    except (TypeError, ValueError):
        uid = -1
    if uid < 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )
    return uid
