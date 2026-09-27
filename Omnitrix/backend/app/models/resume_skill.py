from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text

from app.database.database import Base


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skill_master.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
