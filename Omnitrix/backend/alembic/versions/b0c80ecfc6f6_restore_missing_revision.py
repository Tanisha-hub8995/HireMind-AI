"""restore missing migration marker

Revision ID: b0c80ecfc6f6
Revises: 20260904_add_resume_tables_and_vector
"""

from typing import Sequence, Union


revision: str = "b0c80ecfc6f6"
down_revision: Union[str, Sequence[str], None] = "20260904_add_resume_tables_and_vector"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
