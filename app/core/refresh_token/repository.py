from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.timezone import now_app
from app.core.refresh_token.model import AuthRefreshToken


def insert_token(
    db: Session, *, jti: str, user_id: int, expires_at: datetime
) -> None:
    row = AuthRefreshToken(jti=jti, user_id=user_id, expires_at=expires_at)
    db.add(row)
    db.commit()


def get_active_by_jti(db: Session, jti: str) -> AuthRefreshToken | None:
    stmt = select(AuthRefreshToken).where(
        AuthRefreshToken.jti == jti,
        AuthRefreshToken.revoked_at.is_(None),
    )
    return db.scalars(stmt).first()


def revoke_by_jti(db: Session, jti: str) -> None:
    stmt = (
        update(AuthRefreshToken)
        .where(
            AuthRefreshToken.jti == jti,
            AuthRefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now_app())
    )
    db.execute(stmt)
    db.commit()
