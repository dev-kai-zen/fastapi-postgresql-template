"""add rbac_roles and users

Revision ID: b4e7c2a91d0f
Revises: f1162b8b6331
Create Date: 2026-04-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b4e7c2a91d0f"
down_revision: Union[str, Sequence[str], None] = "f1162b8b6331"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rbac_roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("google_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("picture", sa.String(length=2048), nullable=True),
        sa.Column("id_number", sa.String(length=255), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True, comment="FK to rbac_roles"),
        sa.Column("flags", sa.JSON(), nullable=True),
        sa.Column(
            "is_active",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("last_logged_in", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["rbac_roles.id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("google_id"),
        sa.UniqueConstraint("id_number"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("rbac_roles")
