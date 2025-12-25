from sqlalchemy import Column, String, Integer, Text, ARRAY, ForeignKey, JSON
from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String, ForeignKey("programs.program_id"), nullable=False, index=True)
    code = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    terms = Column(JSON)  # Store as JSON array: ["Fall", "Spring"]
    prereqs = Column(JSON)  # Store as JSON array: ["MATH 212", "BIOE 101"]
    description = Column(Text)
    tags = Column(JSON)  # Store as JSON array: ["core", "bioe"]
    source_url = Column(Text)
