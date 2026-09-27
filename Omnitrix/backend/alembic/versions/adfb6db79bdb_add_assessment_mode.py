"""add assessment mode

Revision ID: adfb6db79bdb
Revises: ebe37dbdc03b
Create Date: 2026-09-23 01:27:31.762871

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "adfb6db79bdb"

down_revision: Union[str, Sequence[str], None] = "ebe37dbdc03b"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass