from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from app.core.security import hash_password
from app.modules.users import repository
from app.modules.users.model import User
from app.modules.users.schema import (
    UserCreate,
    UserGoogleInfo,
    UserListSortBy,
    UserListSortOrder,
    UserListWithRolesResponse,
    UserRead,
    UserUpdate,
    UserWithRolesAndPermissionsResponse,
    UserWithRolesResponse,
)
from app.modules.users.audit_log_client import AuditLogClient
from app.modules.users.rbac_client import RbacClient
from app.modules.audit_logs.schema import AuditLogCreate

_rbac_client = RbacClient()
_audit_log_client = AuditLogClient()


def _user_with_roles_and_permissions_for_user(
    db: Session, user: User
) -> UserWithRolesAndPermissionsResponse:
    roles = _rbac_client.list_rbac_roles_joined_for_user_id(db, user.id)
    role_ids = [r.id for r in roles]
    permissions_raw = _rbac_client.list_rbac_role_permissions_by_role_ids(
        db, role_ids
    )
    seen_perm: set[int] = set()
    permissions: list = []
    for p in permissions_raw:
        if p.permission_id not in seen_perm:
            seen_perm.add(p.permission_id)
            permissions.append(p)
    return UserWithRolesAndPermissionsResponse(
        user=UserRead.model_validate(user),
        roles=roles,
        permissions=permissions,
    )


def _record_user_update_audit(
    db: Session,
    *,
    actor_user_id: int,
    target_user_id: int,
    before: UserRead,
    after: UserRead,
    password_changed: bool,
) -> None:
    print("RECORDING AUDIT LOG FOR USER UPDATE", flush=True)
    """Append an audit row for a successful user update (no secrets in payloads)."""
    b = before.model_dump(mode="json")
    a = after.model_dump(mode="json")
    changed_fields: list[str] = [k for k in a if b.get(k) != a.get(k)]
    if password_changed:
        changed_fields.append("password")
    if not changed_fields:
        return

    old_values: dict = {k: b[k] for k in changed_fields if k != "password"}
    new_values: dict = {k: a[k] for k in changed_fields if k != "password"}
    if password_changed:
        old_values["password"] = "[redacted]"
        new_values["password"] = "[redacted]"

    actor = repository.get_user_by_id(db, actor_user_id)
    actor_email = actor.email if actor is not None else None

    _audit_log_client.create_audit_log(
        db,
        AuditLogCreate(
            user_id=actor_user_id,
            actor_type="user",
            email=actor_email,
            action="update",
            resource_type="user",
            resource_id=str(target_user_id),
            service_name="users",
            old_values=old_values,
            new_values=new_values,
            changed_fields=sorted(changed_fields),
            success=True,
        ),
    )


def _users_with_roles_batch(db: Session, users: list[User]) -> list[UserWithRolesResponse]:
    if not users:
        return []
    user_ids = [u.id for u in users]
    rbac_by_user = _rbac_client.list_rbac_user_roles_by_user_ids(db, user_ids)
    out: list[UserWithRolesResponse] = []
    for u, row in zip(users, rbac_by_user, strict=True):
        out.append(
            UserWithRolesResponse(
                user=UserRead.model_validate(u),
                roles=row.roles,
            )
        )
    return out


def upsert_google_identity(db: Session, data: UserGoogleInfo) -> UserRead:
    """On Google login: update profile + last_login_at if known; otherwise insert."""
    now = datetime.now(UTC)
    existing = repository.get_user_by_google_id(db, data.google_id)
    if existing is not None:
        updated = repository.update_user(
            db,
            existing,
            UserUpdate(
                email=data.email,
                first_name=data.first_name,
                last_name=data.last_name,
                picture=data.picture,
                last_login_at=now,
            ),
        )
        return UserRead.model_validate(updated)

    created = repository.create_user(
        db,
        UserCreate(
            google_id=data.google_id,
            email=data.email,
            first_name=data.first_name or "User",
            last_name=data.last_name or "",
            picture=data.picture,
        )
    )
    created = repository.update_user(
        db,
        created,
        UserUpdate(last_login_at=now),
    )
    return UserRead.model_validate(created)


def list_users(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    sort_by: UserListSortBy = UserListSortBy.ID,
    sort_order: UserListSortOrder = UserListSortOrder.ASC,
    include_deleted: bool = False,
) -> UserListWithRolesResponse:
    total = repository.count_users(
        db, search=search, include_deleted=include_deleted
    )
    rows = repository.get_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        include_deleted=include_deleted,
    )
    data = _users_with_roles_batch(db, rows)
    return UserListWithRolesResponse(data=data, total=total)


def list_users_by_ids(
    db: Session, ids: list[int], *, include_deleted: bool = False
) -> list[UserWithRolesResponse]:
    rows = repository.get_users_by_ids(
        db, ids, include_deleted=include_deleted)
    if not rows:
        return []
    by_id = {u.id: u for u in rows}
    ordered = [by_id[i] for i in ids if i in by_id]
    return _users_with_roles_batch(db, ordered)


def get_user_by_id_with_roles_and_permissions(
    db: Session, user_id: int, *, include_deleted: bool = False
) -> UserWithRolesAndPermissionsResponse:
    user = repository.get_user_by_id(
        db, user_id, include_deleted=include_deleted
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return _user_with_roles_and_permissions_for_user(db, user)


def get_user_by_id(
    db: Session, user_id: int, *, include_deleted: bool = False
) -> UserRead:
    persisted_user = repository.get_user_by_id(
        db, user_id, include_deleted=include_deleted
    )
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserRead.model_validate(persisted_user)


def get_users_by_ids(
    db: Session, ids: list[int], *, include_deleted: bool = False
) -> list[UserRead]:
    persisted_users = repository.get_users_by_ids(
        db, ids, include_deleted=include_deleted
    )
    return [UserRead.model_validate(user) for user in persisted_users]


def create_user(db: Session, create_data: UserCreate) -> UserRead:
    hashed = (
        hash_password(create_data.password) if create_data.password else None
    )
    try:
        persisted_user = repository.create_user(
            db, create_data, hashed_password=hashed
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "User conflicts with existing email, google_id, phone_number, or "
                "username"
            ),
        ) from None
    return UserRead.model_validate(persisted_user)


def update_user_by_id(
    db: Session,
    user_id: int,
    update_data: UserUpdate,
    *,
    actor_user_id: int | None = None,
) -> UserRead:
    persisted_user = repository.get_user_by_id(db, user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    before_read = UserRead.model_validate(persisted_user)
    password_changed = update_data.password is not None
    pwd_hash = (
        hash_password(update_data.password)
        if update_data.password is not None
        else None
    )
    try:
        persisted_user = repository.update_user(
            db, persisted_user, update_data, password_hash=pwd_hash
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "User conflicts with existing email, google_id, phone_number, or "
                "username"
            ),
        ) from None
    after_read = UserRead.model_validate(persisted_user)
    if actor_user_id is not None:
        _record_user_update_audit(
            db,
            actor_user_id=actor_user_id,
            target_user_id=user_id,
            before=before_read,
            after=after_read,
            password_changed=password_changed,
        )
    return after_read


def delete_user_by_id(db: Session, user_id: int) -> None:
    persisted_user = repository.get_user_by_id(db, user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    repository.delete_user(db, persisted_user)
