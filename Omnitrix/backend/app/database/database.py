import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Load variables from .env
load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'app.db'}"


# Get the database URL
DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL

# Neon may provide either postgres:// or postgresql:// URLs.
# SQLAlchemy's psycopg2 dialect uses the postgresql:// form.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = (
        "postgresql+psycopg2://"
        + DATABASE_URL.removeprefix("postgres://")
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = (
        "postgresql+psycopg2://"
        + DATABASE_URL.removeprefix("postgresql://")
    )

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in the .env file."
    )


# Create SQLAlchemy engine
engine_kwargs = {
    "pool_pre_ping": True
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {
        "check_same_thread": False
    }

engine = create_engine(
    DATABASE_URL,
    pool_recycle=1800,
    **engine_kwargs,
)


# Create database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for all SQLAlchemy models
Base = declarative_base()