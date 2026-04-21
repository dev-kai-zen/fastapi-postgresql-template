from collections import defaultdict
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
    UserListWithRbacResponse,
    UserRead,
    UserRolesAndPermissionsResponse,
    UserUpdate,
)
from app.modules.users.rbac_client import RbacClient

_rbac_client = RbacClient()


def _user_roles_and_permissions_for_user(
    db: Session, user: User
) -> UserRolesAndPermissionsResponse:
    user_roles = _rbac_client.list_rbac_user_roles_by_user_id(db, user.id)
    role_ids = list(dict.fromkeys(ur.role_id for ur in user_roles))
    roles = _rbac_client.list_rbac_roles_by_ids(db, role_ids)
    permissions = _rbac_client.list_rbac_role_permissions_by_role_ids(db, role_ids)
    return UserRolesAndPermissionsResponse(
        user=UserRead.model_validate(user),
        roles=roles,
        permissions=permissions,
    )


def _users_with_rbac_batch(
    db: Session, users: list[User]
) -> list[UserRolesAndPermissionsResponse]:
    if not users:
        return []
    user_ids = [u.id for u in users]
    assignments = _rbac_client.list_rbac_user_roles_assignments_for_user_ids(
        db, user_ids
    )
    user_to_role_ids: dict[int, list[int]] = defaultdict(list)
    for a in assignments:
        user_to_role_ids[a.user_id].append(a.role_id)
    all_role_ids = list(dict.fromkeys(a.role_id for a in assignments))
    roles_by_id = {
        r.id: r for r in _rbac_client.list_rbac_roles_by_ids(db, all_role_ids)
    } if all_role_ids else {}
    permissions_all = (
        _rbac_client.list_rbac_role_permissions_by_role_ids(db, all_role_ids)
        if all_role_ids
        else []
    )
    out: list[UserRolesAndPermissionsResponse] = []
    for u in users:
        uid = u.id
        role_ids = list(dict.fromkeys(user_to_role_ids.get(uid, [])))
        roles = [roles_by_id[rid] for rid in role_ids if rid in roles_by_id]
        perms = [p for p in permissions_all if p.role_id in role_ids]
        out.append(
            UserRolesAndPermissionsResponse(
                user=UserRead.model_validate(u),
                roles=roles,
                permissions=perms,
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
        ),
        hashed_password=hash_password(""),
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
) -> UserListWithRbacResponse:
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
    data = _users_with_rbac_batch(db, rows)
    return UserListWithRbacResponse(data=data, total=total)


def list_users_by_ids(
    db: Session, ids: list[int], *, include_deleted: bool = False
) -> list[UserRolesAndPermissionsResponse]:
    rows = repository.get_users_by_ids(db, ids, include_deleted=include_deleted)
    if not rows:
        return []
    by_id = {u.id: u for u in rows}
    ordered = [by_id[i] for i in ids if i in by_id]
    return _users_with_rbac_batch(db, ordered)


def get_users_by_id(
    db: Session, user_id: int, *, include_deleted: bool = False
) -> UserRolesAndPermissionsResponse:
    user = repository.get_user_by_id(
        db, user_id, include_deleted=include_deleted
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return _user_roles_and_permissions_for_user(db, user)


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
        hash_password(create_data.password)
        if create_data.password
        else hash_password("")
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
    db: Session, user_id: int, update_data: UserUpdate
) -> UserRead:
    persisted_user = repository.get_user_by_id(db, user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
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
    return UserRead.model_validate(persisted_user)


def delete_user_by_id(db: Session, user_id: int) -> None:
    persisted_user = repository.get_user_by_id(db, user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    repository.delete_user(db, persisted_user)
