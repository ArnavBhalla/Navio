from sqlalchemy import Column, String, Integer, Text, JSON
from app.core.database import Base


class TrackRequirement(Base):
    __tablename__ = "track_requirements"

    id = Column(Integer, primary_key=True, index=True)
    track = Column(String, unique=True, nullable=False, index=True)  # pre-med, pre-law, etc.
    buckets = Column(JSON, nullable=False)  # Array of bucket objects
    disclaimer = Column(Text)
