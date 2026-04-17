from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    echo=get_settings().debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_development_tables() -> None:
    from app.models import Base

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
