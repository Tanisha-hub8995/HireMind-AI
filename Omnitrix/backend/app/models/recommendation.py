from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rec_type = Column(String(30), nullable=False)  # 'career', 'job', 'skill', 'practice'
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    payload = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    user = relationship("User", backref="recommendations")
