from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.model import User
from app.modules.users.schema import UserCreate, UserUpdate


def get_users(db: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
    stmt = select(User).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_google_id(db: Session, google_id: str) -> User | None:
    stmt = select(User).where(User.google_id == google_id).limit(1)
    return db.scalars(stmt).first()


def create_user(db: Session, obj: UserCreate) -> User:
    db_user = User(
        google_id=obj.google_id,
        email=obj.email,
        password="",
        name=obj.name,
        picture=obj.picture,
        id_number=obj.id_number,
        role_id=obj.role_id,
        flags=obj.flags,
        is_active=obj.is_active,
        last_logged_in=obj.last_logged_in,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, obj: UserUpdate) -> User:
    for key, value in obj.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User) -> None:
    db.delete(db_user)
    db.commit()
