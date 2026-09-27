"""add user roles

Revision ID: 9d9c3c0e2f1a
Revises: 67d47a4c7021
Create Date: 2026-09-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d9c3c0e2f1a"
down_revision: Union[str, Sequence[str], None] = "67d47a4c7021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user")
    )


def downgrade() -> None:
    op.drop_column("users", "role")