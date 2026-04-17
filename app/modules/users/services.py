from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.users import repository
from app.modules.users.schema import UserCreate, UserRead, UserUpdate


def list_users(db: Session, *, skip: int = 0, limit: int = 100) -> list[UserRead]:
    users = repository.get_users(db, skip=skip, limit=limit)
    return [UserRead.model_validate(u) for u in users]


def get_user(db: Session, user_id: int) -> UserRead:
    db_user = repository.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserRead.model_validate(db_user)


def create_user(db: Session, obj: UserCreate) -> UserRead:
    db_user = repository.create_user(db, obj)
    return UserRead.model_validate(db_user)


def update_user(db: Session, user_id: int, obj: UserUpdate) -> UserRead:
    db_user = repository.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db_user = repository.update_user(db, db_user, obj)
    return UserRead.model_validate(db_user)


def delete_user(db: Session, user_id: int) -> None:
    db_user = repository.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    repository.delete_user(db, db_user)
