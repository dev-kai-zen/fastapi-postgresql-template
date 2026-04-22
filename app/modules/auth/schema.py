from pydantic import BaseModel
from dataclasses import dataclass


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    users: dict
    permissions: list[dict]


@dataclass(frozen=True)
class GoogleOAuthCompleteResult(BaseModel):
    token: AccessTokenResponse
    user: dict
    roles: list[dict]
    permissions: list[dict]
