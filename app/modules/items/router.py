from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.items import service
from app.modules.items.schema import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemRead])
def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[ItemRead]:
    return service.list_items(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ItemRead:
    return service.get_item(db, item_id)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(create_data: ItemCreate, db: Session = Depends(get_db)) -> ItemRead:
    return service.create_item(db, create_data)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int, update_data: ItemUpdate, db: Session = Depends(get_db)
) -> ItemRead:
    return service.update_item(db, item_id, update_data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    service.delete_item(db, item_id)
