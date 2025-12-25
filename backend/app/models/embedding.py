from sqlalchemy import Column, String, Integer, Text, JSON
from app.core.database import Base
from app.core.config import settings


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # "course" or "requirement"
    content_text = Column(Text, nullable=False)  # The text that was embedded
    vector = Column(JSON, nullable=False)  # The embedding vector stored as JSON array
    meta_data = Column(JSON)  # {code?, requirement_id?, source_url, etc.}
