from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # e.g., 'interview', 'assessment', 'skill', 'dsa'
    metric_name = Column(String(100), nullable=False)  # e.g., 'average_score', 'interviews_completed'
    value = Column(Float, nullable=False, default=0.0)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    user = relationship("User", backref="progress_records")
