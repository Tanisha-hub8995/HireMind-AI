from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    interview_type = Column(String(30), default="TECHNICAL", nullable=True)  # TECHNICAL, HR, BEHAVIORAL, SYSTEM_DESIGN
    status = Column(String(30), default="SCHEDULED", nullable=True)  # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    user = relationship("User", backref="interviews")
    job = relationship("Job", backref="interviews")
