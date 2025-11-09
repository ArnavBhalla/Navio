from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class TrackRequirement(Base):
    __tablename__ = "track_requirements"

    id = Column(Integer, primary_key=True, index=True)
    track = Column(String, unique=True, nullable=False, index=True)  # pre-med, pre-law, etc.
    buckets = Column(JSONB, nullable=False)  # Array of bucket objects
    disclaimer = Column(Text)
