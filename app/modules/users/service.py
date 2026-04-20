from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.users import repository
from app.modules.users.schema import (
    UserCreate,
    UserGoogleInfo,
    UserListSortBy,
    UserListSortOrder,
    UserPublic,
    UserRead,
    UserUpdate,
    UserListResponse,
)


def upsert_google_identity(db: Session, data: UserGoogleInfo) -> UserPublic:
    """On Google login: update profile + last_logged_in if known; otherwise insert."""
    now = datetime.now(UTC)
    existing = repository.get_user_by_google_id(db, data.google_id)
    if existing is not None:
        updated = repository.update_user(
            db,
            existing,
            UserUpdate(
                email=data.email,
                name=data.name,
                picture=data.picture,
                last_logged_in=now,
            ),
        )
        return UserPublic.model_validate(updated)

    created = repository.create_user(
        db,
        UserCreate(
            google_id=data.google_id,
            email=data.email,
            name=data.name,
            picture=data.picture,
            last_logged_in=now,
        ),
    )
    return UserPublic.model_validate(created)


def list_users(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    sort_by: UserListSortBy = UserListSortBy.ID,
    sort_order: UserListSortOrder = UserListSortOrder.ASC,
) -> UserListResponse:
    total = repository.count_users(db, search=search)
    rows = repository.get_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
    )
    return UserListResponse(
        data=[UserRead.model_validate(row) for row in rows],
        total=total,
    )



def get_user_by_id(db: Session, user_id: int) -> UserRead:
    persisted_user = repository.get_user_by_id(db, user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserRead.model_validate(persisted_user)

def get_users_by_ids(db: Session, ids: list[int]) -> list[UserRead]:
    persisted_users = repository.get_users_by_ids(db, ids)
    return [UserRead.model_validate(user) for user in persisted_users]



def create_user(db: Session, create_data: UserCreate) -> UserRead:
    persisted_user = repository.create_user(db, create_data)
    return UserRead.model_validate(persisted_user)


def update_user(db: Session, user_id: int, update_data: UserUpdate) -> UserRead:
    persisted_user = repository.get_user_by_id(db, user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    persisted_user = repository.update_user(db, persisted_user, update_data)
    return UserRead.model_validate(persisted_user)


def delete_user(db: Session, user_id: int) -> None:
    persisted_user = repository.get_user_by_id(db, user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    repository.delete_user(db, persisted_user)
