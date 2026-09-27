from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class CareerPath(Base):
    __tablename__ = "career_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_role = Column(String(200), nullable=False)
    current_level = Column(String(100), nullable=True)
    target_level = Column(String(100), nullable=True)
    skills_required = Column(JSON, nullable=True)
    skills_acquired = Column(JSON, nullable=True)
    estimated_time_months = Column(Integer, default=6, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    user = relationship("User", backref="career_paths")
