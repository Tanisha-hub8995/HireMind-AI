from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(150), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), nullable=True)  # 'course', 'documentation', 'video', 'practice'
    difficulty = Column(String(20), default="Beginner", nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
