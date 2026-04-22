"""auth refresh tokens table

Revision ID: b4a1c2d3e4f5
Revises: 7088cb5c3e26
Create Date: 2026-04-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b4a1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "7088cb5c3e26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_refresh_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("auth_refresh_tokens_user_id_fkey"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("auth_refresh_tokens_pkey")),
        sa.UniqueConstraint("jti", name=op.f("uq_auth_refresh_tokens_jti")),
    )


def downgrade() -> None:
    op.drop_table("auth_refresh_tokens")
