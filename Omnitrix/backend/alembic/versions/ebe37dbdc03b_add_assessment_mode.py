"""add assessment mode

Revision ID: ebe37dbdc03b
Revises: b0c80ecfc6f6
Create Date: 2026-09-23 01:24:42.026908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebe37dbdc03b'
down_revision: Union[str, Sequence[str], None] = 'b0c80ecfc6f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'assessmentmode'
            ) THEN
                CREATE TYPE assessmentmode AS ENUM (
                    'FULL',
                    'APTITUDE',
                    'ENGLISH',
                    'DSA'
                );
            END IF;
        END
        $$;
    """)

    op.add_column(
        "assessments",
        sa.Column(
            "assessment_mode",
            sa.Enum(
                "FULL",
                "APTITUDE",
                "ENGLISH",
                "DSA",
                name="assessmentmode",
            ),
            nullable=False,
            server_default="FULL",
        ),
    )

    op.create_index(
        "ix_assessments_assessment_mode",
        "assessments",
        ["assessment_mode"],
        unique=False,
    )

    op.alter_column(
        "assessments",
        "assessment_mode",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_assessments_assessment_mode",
        table_name="assessments",
    )

    op.drop_column(
        "assessments",
        "assessment_mode",
    )

    op.execute("""
        DROP TYPE IF EXISTS assessmentmode;
    """)