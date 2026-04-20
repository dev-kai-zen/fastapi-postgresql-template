from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.model import User
from app.modules.users.schema import UserCreate, UserUpdate


def _apply_user_search(query, search: str | None):
    """Same filter for list + count (name, email, id_number must all match — AND)."""
    if search is None:
        return query
    term = search.strip()
    if term == "":
        return query
    pattern = f"%{term}%"
    return query.where(
        User.name.ilike(pattern),
        User.email.ilike(pattern),
        User.id_number.ilike(pattern),
    )


def count_users(db: Session, *, search: str | None = None) -> int:
    query = select(func.count()).select_from(User)
    query = _apply_user_search(query, search)
    return int(db.scalar(query) or 0)


def get_users(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
) -> list[User]:
    query = select(User)
    query = _apply_user_search(query, search)

    # sort_by / sort_order come from validated enums in the API layer
    column = getattr(User, sort_by)
    if sort_order == "desc":
        query = query.order_by(column.desc(), User.id.desc())
    else:
        query = query.order_by(column.asc(), User.id.asc())

    query = query.offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_users_by_ids(db: Session, ids: list[int]) -> list[User]:
    return list(db.scalars(select(User).filter(User.id.in_(ids))).all())

def get_user_by_google_id(db: Session, google_id: str) -> User | None:
    select_statement = select(User).where(User.google_id == google_id).limit(1)
    return db.scalars(select_statement).first()


def create_user(db: Session, create_data: UserCreate) -> User:
    persisted_user = User(
        google_id=create_data.google_id,
        email=create_data.email,
        password="",
        name=create_data.name,
        picture=create_data.picture,
        id_number=create_data.id_number,
        role_id=create_data.role_id,
        flags=create_data.flags,
        is_active=create_data.is_active,
        last_logged_in=create_data.last_logged_in,
    )
    db.add(persisted_user)
    db.commit()
    db.refresh(persisted_user)
    return persisted_user


def update_user(db: Session, persisted_user: User, update_data: UserUpdate) -> User:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(persisted_user, key, value)
    db.add(persisted_user)
    db.commit()
    db.refresh(persisted_user)
    return persisted_user


def delete_user(db: Session, persisted_user: User) -> None:
    db.delete(persisted_user)
    db.commit()
