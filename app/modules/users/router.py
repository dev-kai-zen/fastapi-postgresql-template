from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac_codes import (
    USER_CREATE,
    USER_DELETE,
    USER_READ,
    USER_UPDATE,
)
from app.dependencies.rbac_deps import require_permission
from app.dependencies.token_payload_deps import require_access_token_payload, require_current_user_id
from app.modules.users import service
from app.modules.users.schema import (
    UserCreate,
    UserListSortBy,
    UserListSortOrder,
    UserListWithRolesResponse,
    UserRead,
    UserUpdate,
    UserWithRolesAndPermissionsResponse,
    UserWithRolesResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=UserListWithRolesResponse)
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    sort_by: UserListSortBy = UserListSortBy.ID,
    sort_order: UserListSortOrder = UserListSortOrder.ASC,
    include_deleted: bool = Query(
        default=False,
        description="Include soft-deleted users (`deleted_at` not null).",
    ),
    _: None = Depends(require_permission(USER_READ)),
    db: Session = Depends(get_db),
) -> UserListWithRolesResponse:
    return service.list_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        include_deleted=include_deleted,
    )


@router.get("/get-by-ids", response_model=list[UserWithRolesResponse])
def list_users_by_ids(
    ids: list[int],
    include_deleted: bool = Query(
        default=False,
        description="Include soft-deleted users in the result set.",
    ),
    _: None = Depends(require_permission(USER_READ)),
    db: Session = Depends(get_db),
) -> list[UserWithRolesResponse]:
    return service.list_users_by_ids(db, ids, include_deleted=include_deleted)


# Static segment before /{user_id} so "me" is not captured as a path param.
@router.get("/me", response_model=UserWithRolesAndPermissionsResponse)
def get_user_by_id_with_roles_and_permissions(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_current_user_id),
) -> UserWithRolesAndPermissionsResponse:
    return service.get_user_by_id_with_roles_and_permissions(db, current_user_id)


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    include_deleted: bool = Query(
        default=False,
        description="Allow loading a soft-deleted user by id.",
    ),
    _: None = Depends(require_permission(USER_READ)),
    db: Session = Depends(get_db),
) -> UserRead:
    return service.get_user_by_id(db, user_id, include_deleted=include_deleted)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    create_data: UserCreate,
    _: None = Depends(require_permission(USER_CREATE)),
    db: Session = Depends(get_db),
) -> UserRead:
    return service.create_user(db, create_data)

@router.patch("/{user_id}", response_model=UserRead)
def update_user_by_id(
    user_id: int,
    update_data: UserUpdate,
    _: None = Depends(require_permission(USER_UPDATE)),
    db: Session = Depends(get_db),
) -> UserRead:
    return service.update_user_by_id(db, user_id, update_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    user_id: int,
    _: None = Depends(require_permission(USER_DELETE)),
    db: Session = Depends(get_db),
) -> None:
    service.delete_user_by_id(db, user_id)



