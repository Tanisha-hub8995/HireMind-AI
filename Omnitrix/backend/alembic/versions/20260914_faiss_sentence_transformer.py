"""move embeddings out of PostgreSQL and into FAISS

Revision ID: 20260914_faiss_st
Revises: 20260910_resume_pipeline
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260914_faiss_st"
down_revision: Union[str, Sequence[str], None] = "20260910_resume_pipeline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # FAISS owns vectors; Neon retains resume text and mapping metadata.
    op.execute("ALTER TABLE resumes DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE resume_vectors DROP COLUMN IF EXISTS embedding")


def downgrade() -> None:
    # Restoring vectors requires a model-specific backfill, so do not create
    # misleading columns without rebuilding them from the configured model.
    pass
