"""add section-aware resume vectors

Revision ID: 20260908_add_resume_section_vectors
Revises: b0c80ecfc6f6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260908_resume_sections"
down_revision: Union[str, Sequence[str], None] = "b0c80ecfc6f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("resume_vectors", sa.Column("resume_id", sa.Integer(), nullable=True))
    op.add_column(
        "resume_vectors",
        sa.Column("section_name", sa.String(length=100), nullable=False, server_default="full_resume"),
    )
    op.create_index("ix_resume_vectors_resume_id", "resume_vectors", ["resume_id"], unique=False)
    op.create_index("ix_resume_vectors_section_name", "resume_vectors", ["section_name"], unique=False)
    op.execute("DROP INDEX IF EXISTS ix_resume_vectors_user_id")
    op.create_index("ix_resume_vectors_user_id", "resume_vectors", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_resume_vectors_user_id", table_name="resume_vectors")
    op.drop_index("ix_resume_vectors_section_name", table_name="resume_vectors")
    op.drop_index("ix_resume_vectors_resume_id", table_name="resume_vectors")
    op.drop_column("resume_vectors", "section_name")
    op.drop_column("resume_vectors", "resume_id")
