from sqlalchemy.orm import Session


from app.modules.auth import service as auth_service
from app.core.db import get_db
from app.core.constants import REFRESH_TOKEN_COOKIE_NAME
from fastapi import Depends, Cookie


class AuthClient:
    def __init__(self):
        self.db = Depends(get_db)
        self.refresh_token = Cookie(..., alias=REFRESH_TOKEN_COOKIE_NAME)

    def refresh_access_token(self) -> dict:
        return auth_service.refresh_access_token(self.db, self.refresh_token)
