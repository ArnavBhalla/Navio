from sqlalchemy import Column, String, Integer, Text
from app.core.database import Base


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String, unique=True, index=True, nullable=False)
    university = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    major = Column(String, nullable=False)
    version_year = Column(Integer, nullable=False)
    catalog_url = Column(Text)
    notes = Column(Text)
