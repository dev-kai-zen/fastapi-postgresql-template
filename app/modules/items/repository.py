from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.items.model import Items
from app.modules.items.schema import ItemCreate, ItemUpdate


def get_items(db: Session, *, skip: int = 0, limit: int = 100) -> list[Items]:
    select_statement = (
        select(Items)
        .where(Items.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(select_statement).all())


def get_item(db: Session, item_id: int) -> Items | None:
    persisted_item = db.get(Items, item_id)
    if persisted_item is None or persisted_item.deleted_at is not None:
        return None
    return persisted_item


def create_item(db: Session, create_data: ItemCreate) -> Items:
    persisted_item = Items(title=create_data.title, description=create_data.description)
    db.add(persisted_item)
    db.commit()
    db.refresh(persisted_item)
    return persisted_item


def update_item(db: Session, persisted_item: Items, update_data: ItemUpdate) -> Items:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(persisted_item, key, value)
    db.add(persisted_item)
    db.commit()
    db.refresh(persisted_item)
    return persisted_item


def delete_item(db: Session, persisted_item: Items) -> None:
    db.delete(persisted_item)
    db.commit()
