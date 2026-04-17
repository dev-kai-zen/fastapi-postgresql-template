from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.users import services
from app.modules.users.schema import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[UserRead]:
    return services.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    return services.get_user(db, user_id)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(obj: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    return services.create_user(db, obj)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, obj: UserUpdate, db: Session = Depends(get_db)
) -> UserRead:
    return services.update_user(db, user_id, obj)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    services.delete_user(db, user_id)
