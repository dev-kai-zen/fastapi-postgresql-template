from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.items.model import Items
from app.modules.items.schema import ItemCreate, ItemUpdate


def get_items(db: Session, *, skip: int = 0, limit: int = 100) -> list[Items]:
    stmt = (
        select(Items)
        .where(Items.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_item(db: Session, item_id: int) -> Items | None:
    row = db.get(Items, item_id)
    if row is None or row.deleted_at is not None:
        return None
    return row


def create_item(db: Session, obj: ItemCreate) -> Items:
    db_item = Items(title=obj.title, description=obj.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, db_item: Items, obj: ItemUpdate) -> Items:
    for key, value in obj.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, db_item: Items) -> None:
    db.delete(db_item)
    db.commit()
