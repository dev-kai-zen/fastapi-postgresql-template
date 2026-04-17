from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.items import repository
from app.modules.items.schema import ItemCreate, ItemRead, ItemUpdate


def list_items(db: Session, *, skip: int = 0, limit: int = 100) -> list[ItemRead]:
    items = repository.get_items(db, skip=skip, limit=limit)
    return [ItemRead.model_validate(i) for i in items]


def get_item(db: Session, item_id: int) -> ItemRead:
    db_item = repository.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return ItemRead.model_validate(db_item)


def create_item(db: Session, obj: ItemCreate) -> ItemRead:
    db_item = repository.create_item(db, obj)
    return ItemRead.model_validate(db_item)


def update_item(db: Session, item_id: int, obj: ItemUpdate) -> ItemRead:
    db_item = repository.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    db_item = repository.update_item(db, db_item, obj)
    return ItemRead.model_validate(db_item)


def delete_item(db: Session, item_id: int) -> None:
    db_item = repository.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    repository.delete_item(db, db_item)
