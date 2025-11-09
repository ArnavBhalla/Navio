from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String, ForeignKey("programs.program_id"), nullable=False, index=True)
    requirement_id = Column(String, nullable=False, index=True)  # e.g., "bioe-core-1"
    type = Column(String, nullable=False)  # AND, OR, ELECTIVE_GROUP, DISTRIBUTION
    description = Column(Text)
    rules = Column(JSONB, nullable=False)  # Nested rules structure
    text_source = Column(Text)
    source_url = Column(Text)
