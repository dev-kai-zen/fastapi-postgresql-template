from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.timezone import now_app
from app.modules.users.model import User
from app.modules.users.schema import UserCreate, UserUpdate


def _filter_deleted(query, *, include_deleted: bool):
    """By default exclude rows with `deleted_at` set; include them when `include_deleted` is True."""
    if include_deleted:
        return query
    return query.where(User.deleted_at.is_(None))


def _apply_user_search(query, search: str | None):
    """Filter rows where any of several fields matches the search term (OR)."""
    if search is None:
        return query
    term = search.strip()
    if term == "":
        return query
    pattern = f"%{term}%"
    return query.where(
        or_(
            User.first_name.ilike(pattern),
            User.last_name.ilike(pattern),
            User.middle_name.ilike(pattern),
            User.email.ilike(pattern),
            User.phone_number.ilike(pattern),
            User.username.ilike(pattern),
            User.google_id.ilike(pattern),
        )
    )


def count_users(
    db: Session, *, search: str | None = None, include_deleted: bool = False
) -> int:
    query = select(func.count()).select_from(User)
    query = _filter_deleted(query, include_deleted=include_deleted)
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
    include_deleted: bool = False,
) -> list[User]:
    query = select(User)
    query = _filter_deleted(query, include_deleted=include_deleted)
    query = _apply_user_search(query, search)

    column = getattr(User, sort_by)
    if sort_order == "desc":
        query = query.order_by(column.desc(), User.id.desc())
    else:
        query = query.order_by(column.asc(), User.id.asc())

    query = query.offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_user_by_id(
    db: Session, user_id: int, *, include_deleted: bool = False
) -> User | None:
    row = db.get(User, user_id)
    if row is None:
        return None
    if not include_deleted and row.deleted_at is not None:
        return None
    return row


def get_user_by_id_with_roles_and_permissions(
    db: Session, user_id: int, *, include_deleted: bool = False
) -> User | None:
    row = db.get(User, user_id)
    if row is None:
        return None
    if not include_deleted and row.deleted_at is not None:
        return None
    return row

    
def get_users_by_ids(
    db: Session, ids: list[int], *, include_deleted: bool = False
) -> list[User]:
    if not ids:
        return []
    stmt = select(User).where(User.id.in_(ids))
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return list(db.scalars(stmt).all())


def get_user_by_google_id(db: Session, google_id: str, *, include_deleted: bool = False) -> User | None:
    select_statement = (
        select(User)
        .where(User.google_id == google_id)
        .limit(1)
    )
    if not include_deleted:
        select_statement = select_statement.where(User.deleted_at.is_(None))
    return db.scalars(select_statement).first()


def create_user(db: Session, create_data: UserCreate, *, hashed_password: str) -> User:
    persisted_user = User(
        google_id=create_data.google_id,
        email=create_data.email,
        phone_number=create_data.phone_number,
        first_name=create_data.first_name,
        middle_name=create_data.middle_name,
        last_name=create_data.last_name,
        username=create_data.username,
        hashed_password=hashed_password,
        picture=create_data.picture,
        is_active=create_data.is_active,
    )
    db.add(persisted_user)
    db.commit()
    db.refresh(persisted_user)
    return persisted_user


def update_user(
    db: Session,
    persisted_user: User,
    update_data: UserUpdate,
    *,
    password_hash: str | None = None,
) -> User:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        if key == "password":
            continue
        setattr(persisted_user, key, value)
    if password_hash is not None:
        persisted_user.hashed_password = password_hash
    db.add(persisted_user)
    db.commit()
    db.refresh(persisted_user)
    return persisted_user


def delete_user(db: Session, persisted_user: User) -> None:
    persisted_user.deleted_at = now_app()
    db.add(persisted_user)
    db.commit()
    db.refresh(persisted_user)
