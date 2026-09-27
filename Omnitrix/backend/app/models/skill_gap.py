from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    skill_name = Column(String(150), nullable=False)
    gap_level = Column(String(20), default="medium", nullable=True)  # 'low', 'medium', 'high', 'critical'
    target_role = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    user = relationship("User", backref="skill_gaps")
    resume = relationship("Resume", backref="skill_gaps")
