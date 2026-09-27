from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.database.enums import (
    AssessmentMode,
    AssessmentSection,
    AssessmentStatus,
    QuestionStatus,
)


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(SQLEnum(AssessmentStatus, name="assessmentstatus"), default=AssessmentStatus.NOT_STARTED, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    total_score = Column(Float, default=0.0, nullable=True)
    maximum_score = Column(Float, default=0.0, nullable=True)
    percentage = Column(Float, default=0.0, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    assessment_mode = Column(SQLEnum(AssessmentMode, name="assessmentmode"), default=AssessmentMode.FULL, nullable=True)

    user = relationship("User", backref="assessments")
    answers = relationship("AssessmentAnswer", backref="assessment", cascade="all, delete-orphan")
    section_results = relationship("AssessmentSectionResult", backref="assessment", cascade="all, delete-orphan")
    results = relationship("AssessmentResult", backref="assessment", cascade="all, delete-orphan")


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    section_id = Column(Integer, nullable=True)
    selected_option = Column(String(1), nullable=True)
    status = Column(SQLEnum(QuestionStatus, name="questionstatus"), default=QuestionStatus.UNSEEN, nullable=True)
    visited_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Integer, default=0, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    marks_awarded = Column(Float, default=0.0, nullable=True)

    question = relationship("Question")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    total_score = Column(Float, default=0.0, nullable=True)
    maximum_score = Column(Float, default=0.0, nullable=True)
    percentage = Column(Float, default=0.0, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)


class AssessmentSectionResult(Base):
    __tablename__ = "assessment_section_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False, index=True)
    section = Column(SQLEnum(AssessmentSection, name="assessmentsection"), nullable=False)
    started_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    score = Column(Float, default=0.0, nullable=True)
    maximum_score = Column(Float, default=0.0, nullable=True)
    percentage = Column(Float, default=0.0, nullable=True)
    correct_count = Column(Integer, default=0, nullable=True)
    wrong_count = Column(Integer, default=0, nullable=True)
    skipped_count = Column(Integer, default=0, nullable=True)
    attempted_count = Column(Integer, default=0, nullable=True)
    accuracy = Column(Float, default=0.0, nullable=True)
    time_efficiency = Column(Float, default=0.0, nullable=True)
    difficulty_score = Column(Float, default=0.0, nullable=True)
