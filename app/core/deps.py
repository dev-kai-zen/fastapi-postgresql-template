"""
Protected-route auth dependency.

Flow (browser SPA): access JWT in ``Authorization: Bearer``; refresh JWT in HttpOnly cookie.
1. If access is valid → return its payload.
2. If access is **expired** → require refresh cookie; verify refresh (signature, ``exp``, revoke list);
   if valid → mint new access JWT, set ``X-New-Access-Token`` on the response, return new payload.
3. If access is invalid (not just expired), or refresh missing/invalid/expired → **401** (client
   should clear local storage and send the user to login).
"""

import jwt
from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.constants import NEW_ACCESS_TOKEN_HEADER, REFRESH_TOKEN_COOKIE_NAME
from app.core.security import decode_access_token, refresh_access_token

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
        new_access = refresh_access_token(refresh_token)
        response.headers[NEW_ACCESS_TOKEN_HEADER] = new_access
        return decode_access_token(new_access)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )
