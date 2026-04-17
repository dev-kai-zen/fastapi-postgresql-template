from fastapi import APIRouter, Depends

from app.core.config import get_settings

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import cast
from app.core.db import get_db
import redis
from typing import Callable
from app.core.redis_client import get_redis

router = APIRouter()


@router.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"Connected to the API: {get_settings().app_name}"}


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "Healthy", "service": settings.app_name}


@router.get("/db-ping")
def db_ping(db: Session = Depends(get_db)) -> dict[str, bool | int]:
    one = cast(int, db.execute(text("SELECT 1")).scalar_one())
    return {"ok": True, "select_1": one}


@router.get("/redis-ping")
def redis_ping(r: redis.Redis = Depends(get_redis)):
    # Yes, even when using a shared pool, you use the dependency the same way.
    pong = cast(Callable[[], bool], r.ping)()
    return {"ok": True, "ping": pong}
