from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.users import service
from app.modules.users.schema import (
    UserCreate,
    UserListSortBy,
    UserListSortOrder,
    UserRead,
    UserUpdate,
    UserListResponse,
)

from app.core.deps import require_access_token_payload

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(require_access_token_payload)])


@router.get("", response_model=UserListResponse)
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    sort_by: UserListSortBy = UserListSortBy.ID,
    sort_order: UserListSortOrder = UserListSortOrder.ASC,
    db: Session = Depends(get_db),
) -> UserListResponse:
    users = service.list_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return users


@router.get("/get-by-ids", response_model=list[UserRead])
def get_users_by_ids(ids: list[int], db: Session = Depends(get_db)) -> list[UserRead]:
    return service.get_users_by_ids(db, ids)


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    return service.get_user_by_id(db, user_id)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(create_data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    return service.create_user(db, create_data)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)
) -> UserRead:
    return service.update_user(db, user_id, update_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    service.delete_user(db, user_id)
