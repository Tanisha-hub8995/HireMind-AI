from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    required_skills = Column(JSON, nullable=True)
    location = Column(String(200), nullable=True)
    salary_range = Column(String(100), nullable=True)
    job_type = Column(String(50), nullable=True)
    status = Column(String(30), default="active", nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    company = relationship("Company", backref="jobs", lazy="joined")
