from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from app.database.database import Base


class Skill(Base):
    __tablename__ = "skill_master"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(150), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=True)
    aliases = Column(JSON, nullable=True, default=list)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
