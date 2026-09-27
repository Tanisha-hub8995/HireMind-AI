"""add complete schema: companies, jobs, interviews, questions, answers,
assessments, interview_results, career_paths, user_progress,
recommendations, learning_resources, skill_gaps

Revision ID: 20260924_complete_schema
Revises: adfb6db79bdb
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260924_complete_schema"
down_revision: Union[str, Sequence[str], None] = "adfb6db79bdb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # ------------------------------------------------------------------ companies
    if "companies" not in existing_tables:
        op.create_table(
            "companies",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("industry", sa.String(100), nullable=True),
            sa.Column("website", sa.String(300), nullable=True),
            sa.Column("location", sa.String(200), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("size", sa.String(50), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_companies_id", "companies", ["id"])
        op.create_index("ix_companies_name", "companies", ["name"])

    # ------------------------------------------------------------------ jobs
    if "jobs" not in existing_tables:
        op.create_table(
            "jobs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("required_skills", sa.JSON(), nullable=True),
            sa.Column("location", sa.String(200), nullable=True),
            sa.Column("salary_range", sa.String(100), nullable=True),
            sa.Column("job_type", sa.String(50), nullable=True),
            sa.Column("status", sa.String(30), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_jobs_id", "jobs", ["id"])
        op.create_index("ix_jobs_company_id", "jobs", ["company_id"])

    # ------------------------------------------------------------------ interviews
    if "interviews" not in existing_tables:
        op.create_table(
            "interviews",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=True),
            sa.Column("interview_type", sa.String(30), nullable=False, server_default="mixed"),
            sa.Column("status", sa.String(30), nullable=False, server_default="scheduled"),
            sa.Column("score", sa.Float(), nullable=True),
            sa.Column("feedback", sa.Text(), nullable=True),
            sa.Column("scheduled_at", sa.DateTime(), nullable=True),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_interviews_id", "interviews", ["id"])
        op.create_index("ix_interviews_user_id", "interviews", ["user_id"])
        op.create_index("ix_interviews_job_id", "interviews", ["job_id"])

    # ------------------------------------------------------------------ questions
    if "questions" not in existing_tables:
        op.create_table(
            "questions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("interview_id", sa.Integer(), sa.ForeignKey("interviews.id"), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("question_type", sa.String(30), nullable=False, server_default="technical"),
            sa.Column("difficulty", sa.String(20), nullable=True, server_default="medium"),
            sa.Column("topic", sa.String(100), nullable=True),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_questions_id", "questions", ["id"])
        op.create_index("ix_questions_interview_id", "questions", ["interview_id"])

    # ------------------------------------------------------------------ answers
    if "answers" not in existing_tables:
        op.create_table(
            "answers",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("answer_text", sa.Text(), nullable=True),
            sa.Column("audio_path", sa.String(500), nullable=True),
            sa.Column("score", sa.Float(), nullable=True),
            sa.Column("feedback", sa.Text(), nullable=True),
            sa.Column("keywords_detected", sa.JSON(), nullable=True),
            sa.Column("time_taken_seconds", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_answers_id", "answers", ["id"])
        op.create_index("ix_answers_question_id", "answers", ["question_id"])
        op.create_index("ix_answers_user_id", "answers", ["user_id"])

    # ------------------------------------------------------------------ assessments
    if "assessments" not in existing_tables:
        op.create_table(
            "assessments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("category", sa.String(100), nullable=True),
            sa.Column("total_score", sa.Float(), nullable=True),
            sa.Column("max_score", sa.Float(), nullable=False, server_default="100"),
            sa.Column("passed", sa.Boolean(), nullable=True),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_assessments_id", "assessments", ["id"])
        op.create_index("ix_assessments_user_id", "assessments", ["user_id"])

    # ------------------------------------------------------------------ interview_results
    if "interview_results" not in existing_tables:
        op.create_table(
            "interview_results",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("interview_id", sa.Integer(), sa.ForeignKey("interviews.id"), nullable=False, unique=True),
            sa.Column("overall_score", sa.Float(), nullable=True),
            sa.Column("technical_score", sa.Float(), nullable=True),
            sa.Column("communication_score", sa.Float(), nullable=True),
            sa.Column("confidence_score", sa.Float(), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("strengths", sa.JSON(), nullable=True),
            sa.Column("improvements", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_interview_results_id", "interview_results", ["id"])
        op.create_index("ix_interview_results_interview_id", "interview_results", ["interview_id"])

    # ------------------------------------------------------------------ career_paths
    if "career_paths" not in existing_tables:
        op.create_table(
            "career_paths",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("target_role", sa.String(200), nullable=False),
            sa.Column("current_level", sa.String(100), nullable=True),
            sa.Column("target_level", sa.String(100), nullable=True),
            sa.Column("skills_required", sa.JSON(), nullable=True),
            sa.Column("skills_acquired", sa.JSON(), nullable=True),
            sa.Column("estimated_time_months", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_career_paths_id", "career_paths", ["id"])
        op.create_index("ix_career_paths_user_id", "career_paths", ["user_id"])

    # ------------------------------------------------------------------ user_progress
    if "user_progress" not in existing_tables:
        op.create_table(
            "user_progress",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("category", sa.String(50), nullable=False),
            sa.Column("metric_name", sa.String(100), nullable=False),
            sa.Column("value", sa.Float(), nullable=False, server_default="0"),
            sa.Column("recorded_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_user_progress_id", "user_progress", ["id"])
        op.create_index("ix_user_progress_user_id", "user_progress", ["user_id"])

    # ------------------------------------------------------------------ recommendations
    if "recommendations" not in existing_tables:
        op.create_table(
            "recommendations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("rec_type", sa.String(30), nullable=False),
            sa.Column("title", sa.String(300), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("score", sa.Float(), nullable=True),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_recommendations_id", "recommendations", ["id"])
        op.create_index("ix_recommendations_user_id", "recommendations", ["user_id"])

    # ------------------------------------------------------------------ learning_resources
    if "learning_resources" not in existing_tables:
        op.create_table(
            "learning_resources",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("skill_name", sa.String(150), nullable=False),
            sa.Column("title", sa.String(300), nullable=False),
            sa.Column("url", sa.String(500), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("resource_type", sa.String(50), nullable=True),
            sa.Column("difficulty", sa.String(20), nullable=True, server_default="beginner"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_learning_resources_id", "learning_resources", ["id"])
        op.create_index("ix_learning_resources_skill_name", "learning_resources", ["skill_name"])

    # ------------------------------------------------------------------ skill_gaps
    if "skill_gaps" not in existing_tables:
        op.create_table(
            "skill_gaps",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id"), nullable=True),
            sa.Column("skill_name", sa.String(150), nullable=False),
            sa.Column("gap_level", sa.String(20), nullable=False, server_default="medium"),
            sa.Column("target_role", sa.String(200), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_skill_gaps_id", "skill_gaps", ["id"])
        op.create_index("ix_skill_gaps_user_id", "skill_gaps", ["user_id"])
        op.create_index("ix_skill_gaps_resume_id", "skill_gaps", ["resume_id"])


def downgrade() -> None:
    op.drop_table("skill_gaps")
    op.drop_table("learning_resources")
    op.drop_table("recommendations")
    op.drop_table("user_progress")
    op.drop_table("career_paths")
    op.drop_table("interview_results")
    op.drop_table("assessments")
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("interviews")
    op.drop_table("jobs")
    op.drop_table("companies")
