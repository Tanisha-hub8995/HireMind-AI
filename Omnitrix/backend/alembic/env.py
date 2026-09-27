from logging.config import fileConfig

from sqlalchemy import engine_from_config, text
from sqlalchemy import pool

from alembic import context

# --------------------------------------------------
# Import database Base and DATABASE_URL
# --------------------------------------------------

from app.database.database import Base, DATABASE_URL

# --------------------------------------------------
# Import ALL SQLAlchemy models
# --------------------------------------------------

# Existing models
from app.models import Resume, ResumeVector, User  # noqa: F401

# Assessment models
from app.models.assessment import Assessment  # noqa: F401
from app.models.assessment_section import AssessmentSectionResult  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.answer import AssessmentAnswer  # noqa: F401
from app.models.result import AssessmentResult  # noqa: F401

# --------------------------------------------------
# Alembic Config object
# --------------------------------------------------

config = context.config

# --------------------------------------------------
# Tell Alembic which database to use
# --------------------------------------------------

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%")
)

# --------------------------------------------------
# Configure logging
# --------------------------------------------------

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --------------------------------------------------
# SQLAlchemy metadata
# --------------------------------------------------

target_metadata = Base.metadata

# --------------------------------------------------
# Offline migrations
# --------------------------------------------------


def run_migrations_offline() -> None:
    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------
# Online migrations
# --------------------------------------------------


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        if connection.dialect.name == "postgresql":
            connection.execute(
                text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                )
            )
            connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------------------------
# Run migration
# --------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()