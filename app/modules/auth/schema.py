from typing import Any

from pydantic import BaseModel, ConfigDict


class AuthUserIdentity(BaseModel):
    """Snapshot after Google upsert for JWTs; owned by auth (not users.schema types)."""

    model_config = ConfigDict(frozen=True)

    id: int
    role_id: int | None
    user_claims: dict[str, Any]


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    users: dict
    permissions: list[dict]
