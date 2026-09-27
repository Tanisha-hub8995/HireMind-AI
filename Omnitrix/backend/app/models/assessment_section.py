from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum
)

from sqlalchemy.orm import relationship

from app.database.database import Base

from app.database.enums import (
    AssessmentSection
)


class AssessmentSectionResult(Base):

    __tablename__ = "assessment_section_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id"),
        nullable=False
    )

    section = Column(
        SQLEnum(AssessmentSection),
        nullable=False
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    deadline = Column(
        DateTime(timezone=True),
        nullable=True
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # -------------------------------
    # SCORE
    # -------------------------------

    score = Column(
        Float,
        default=0.0,
        nullable=False
    )

    maximum_score = Column(
        Float,
        default=0.0,
        nullable=False
    )

    percentage = Column(
        Float,
        default=0.0,
        nullable=False
    )

    # -------------------------------
    # COUNTS
    # -------------------------------

    correct_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    wrong_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    skipped_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    attempted_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    # -------------------------------
    # PERFORMANCE
    # -------------------------------

    accuracy = Column(
        Float,
        default=0.0,
        nullable=False
    )

    time_efficiency = Column(
        Float,
        default=0.0,
        nullable=False
    )

    difficulty_score = Column(
        Float,
        default=0.0,
        nullable=False
    )

    # -------------------------------
    # RELATIONSHIP
    # -------------------------------

    assessment = relationship(
        "Assessment",
        back_populates="sections"
    )