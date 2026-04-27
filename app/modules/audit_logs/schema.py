from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator


class AuditLogListSortBy(StrEnum):
    """Allowed `sort_by` values (must match `AuditLog` columns used in the repository)."""

    ID = "id"
    CREATED_AT = "created_at"
    OCCURRED_AT = "occurred_at"
    EMAIL = "email"
    ACTION = "action"
    RESOURCE_TYPE = "resource_type"
    SUCCESS = "success"


class AuditLogListSortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class AuditLogCreate(BaseModel):
    """Payload to append one audit row (`created_at` is set by the database)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    occurred_at: datetime | None = None
    user_id: int | None = None
    actor_type: str = Field(default="user", max_length=32)
    email: str | None = Field(default=None, max_length=320)
    action: str = Field(max_length=64)
    resource_type: str = Field(max_length=128)
    resource_id: str | None = Field(default=None, max_length=64)
    service_name: str = Field(max_length=255)
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    changed_fields: list[str] | None = None
    tenant_id: str | None = Field(default=None, max_length=64)
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = Field(default=None, max_length=64)
    correlation_id: str | None = Field(default=None, max_length=64)
    success: bool = True
    error_message: str | None = None
    extra: dict[str, Any] | None = None

    @model_validator(mode="after")
    def blank_ip_to_none(self) -> "AuditLogCreate":
        if self.ip_address is not None and not str(self.ip_address).strip():
            return self.model_copy(update={"ip_address": None})
        return self


class AuditLogRead(BaseModel):
    """Full audit row returned from list and get-by-id."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    occurred_at: datetime | None
    user_id: int | None
    actor_type: str
    email: str | None
    action: str
    resource_type: str
    resource_id: str | None
    service_name: str
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    changed_fields: list[str] | None
    tenant_id: str | None
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    correlation_id: str | None
    success: bool
    error_message: str | None
    extra: dict[str, Any] | None

    @field_serializer("ip_address")
    def serialize_ip(self, value: object) -> str | None:
        if value is None:
            return None
        return str(value)


class AuditLogListResponse(BaseModel):
    data: list[AuditLogRead]
    total: int
