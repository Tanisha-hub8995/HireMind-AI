"""add resume tables — FAISS replaces pgvector

Revision ID: 20260904_add_resume_tables_and_vector
Revises: 9d9c3c0e2f1a
Create Date: 2026-09-04 00:00:00.000000

NOTE: The original revision used pgvector with a hardcoded 64-dimensional
Vector(64) column. We now use FAISS (faiss-cpu) with SentenceTransformer
embeddings stored in a local .faiss index file. PostgreSQL only stores the
text content and metadata; the pgvector extension and embedding columns are
NOT required.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260904_add_resume_tables_and_vector"
down_revision: Union[str, Sequence[str], None] = "9d9c3c0e2f1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if "resumes" not in existing:
        op.create_table(
            "resumes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("file_name", sa.String(length=255), nullable=True),
            sa.Column("file_type", sa.String(length=50), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("raw_text", sa.Text(), nullable=True),
            sa.Column("extracted_skills", sa.JSON(), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            # No embedding column — vectors are stored in FAISS, not PostgreSQL
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_resumes_id"), "resumes", ["id"], unique=False)
        op.create_index(op.f("ix_resumes_user_id"), "resumes", ["user_id"], unique=False)

    if "resume_vectors" not in existing:
        op.create_table(
            "resume_vectors",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("resume_id", sa.Integer(), nullable=True),
            sa.Column("section_name", sa.String(length=100), nullable=False, server_default="resume"),
            sa.Column("text_content", sa.Text(), nullable=False),
            sa.Column("metadata", sa.JSON(), nullable=True),
            # No embedding column — vectors are managed by FAISS using
            # sentence-transformers/all-MiniLM-L6-v2 (384-dim), NOT pgvector
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_resume_vectors_id"), "resume_vectors", ["id"], unique=False)
        op.create_index(op.f("ix_resume_vectors_user_id"), "resume_vectors", ["user_id"], unique=False)
        op.create_index(op.f("ix_resume_vectors_resume_id"), "resume_vectors", ["resume_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_resume_vectors_resume_id"), table_name="resume_vectors")
    op.drop_index(op.f("ix_resume_vectors_user_id"), table_name="resume_vectors")
    op.drop_index(op.f("ix_resume_vectors_id"), table_name="resume_vectors")
    op.drop_table("resume_vectors")
    op.drop_index(op.f("ix_resumes_user_id"), table_name="resumes")
    op.drop_index(op.f("ix_resumes_id"), table_name="resumes")
    op.drop_table("resumes")
