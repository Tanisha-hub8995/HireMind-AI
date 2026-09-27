"""stub for revision adfb6db79bdb — already applied in Neon

This revision exists in the Neon database's alembic_version table but its
migration file was not present in the local repository.  This stub allows
Alembic to resolve the revision chain and continue upgrading without error.

Revision ID: adfb6db79bdb
Revises: 20260914_faiss_st
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "adfb6db79bdb"
down_revision: Union[str, Sequence[str], None] = "20260914_faiss_st"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Already applied in Neon — no-op stub.
    pass


def downgrade() -> None:
    pass
