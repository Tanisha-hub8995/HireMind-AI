"""add durable resume processing and skill tables

Revision ID: 20260910_resume_pipeline
Revises: 20260908_resume_sections
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260910_resume_pipeline"
down_revision: Union[str, Sequence[str], None] = "20260908_resume_sections"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    resume_columns = {column["name"] for column in inspector.get_columns("resumes")}
    for name, column in {
        "original_filename": sa.Column("original_filename", sa.String(length=255), nullable=True),
        "stored_filename": sa.Column("stored_filename", sa.String(length=255), nullable=True),
        "file_path": sa.Column("file_path", sa.String(length=500), nullable=True),
        "processing_status": sa.Column("processing_status", sa.String(length=30), nullable=False, server_default="uploaded"),
    }.items():
        if name not in resume_columns:
            op.add_column("resumes", column)

    if "skill_master" not in inspector.get_table_names():
        op.create_table(
            "skill_master",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("canonical_name", sa.String(length=150), nullable=False),
            sa.Column("category", sa.String(length=100), nullable=True),
            sa.Column("aliases", sa.JSON(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_skill_master_id", "skill_master", ["id"])
        op.create_index("ix_skill_master_canonical_name", "skill_master", ["canonical_name"], unique=True)

    if "resume_sections" not in inspector.get_table_names():
        op.create_table(
            "resume_sections",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("section_type", sa.String(length=50), nullable=False),
            sa.Column("section_text", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_resume_sections_id", "resume_sections", ["id"])
        op.create_index("ix_resume_sections_resume_id", "resume_sections", ["resume_id"])
        op.create_index("ix_resume_sections_section_type", "resume_sections", ["section_type"])

    if "resume_skills" not in inspector.get_table_names():
        op.create_table(
            "resume_skills",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skill_master.id", ondelete="CASCADE"), nullable=False),
            sa.Column("evidence", sa.Text(), nullable=True),
            sa.Column("confidence", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_resume_skills_id", "resume_skills", ["id"])
        op.create_index("ix_resume_skills_resume_id", "resume_skills", ["resume_id"])
        op.create_index("ix_resume_skills_skill_id", "resume_skills", ["skill_id"])


def downgrade() -> None:
    op.drop_table("resume_skills")
    op.drop_table("resume_sections")
    op.drop_table("skill_master")
    op.drop_column("resumes", "processing_status")
    op.drop_column("resumes", "file_path")
    op.drop_column("resumes", "stored_filename")
    op.drop_column("resumes", "original_filename")
