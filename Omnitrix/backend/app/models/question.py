from sqlalchemy import Boolean, Column, Float, Integer, String, Text, Enum as SQLEnum

from app.database.database import Base
from app.database.enums import AssessmentSection, DifficultyLevel


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    section = Column(SQLEnum(AssessmentSection, name="assessmentsection"), nullable=True, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=True)
    option_b = Column(String(500), nullable=True)
    option_c = Column(String(500), nullable=True)
    option_d = Column(String(500), nullable=True)
    correct_option = Column(String(1), nullable=True)  # 'A', 'B', 'C', 'D'
    difficulty = Column(SQLEnum(DifficultyLevel, name="difficultylevel"), default=DifficultyLevel.MEDIUM, nullable=True)
    expected_time_seconds = Column(Integer, default=60, nullable=True)
    positive_mark = Column(Float, default=1.0, nullable=True)
    negative_mark = Column(Float, default=0.0, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
