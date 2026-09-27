from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(300), nullable=True)
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    size = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
