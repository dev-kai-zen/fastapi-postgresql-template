from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.items import repository
from app.modules.items.schema import ItemCreate, ItemRead, ItemUpdate


def list_items(db: Session, *, skip: int = 0, limit: int = 100) -> list[ItemRead]:
    items = repository.get_items(db, skip=skip, limit=limit)
    return [ItemRead.model_validate(item) for item in items]


def get_item(db: Session, item_id: int) -> ItemRead:
    persisted_item = repository.get_item(db, item_id)
    if persisted_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return ItemRead.model_validate(persisted_item)


def create_item(db: Session, create_data: ItemCreate) -> ItemRead:
    persisted_item = repository.create_item(db, create_data)
    return ItemRead.model_validate(persisted_item)


def update_item(db: Session, item_id: int, update_data: ItemUpdate) -> ItemRead:
    persisted_item = repository.get_item(db, item_id)
    if persisted_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    persisted_item = repository.update_item(db, persisted_item, update_data)
    return ItemRead.model_validate(persisted_item)


def delete_item(db: Session, item_id: int) -> None:
    persisted_item = repository.get_item(db, item_id)
    if persisted_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    repository.delete_item(db, persisted_item)
