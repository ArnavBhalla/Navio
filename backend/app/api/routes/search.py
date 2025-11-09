"""
Course search API endpoint
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.rag import RAGService
from pydantic import BaseModel


class CourseSearchResult(BaseModel):
    code: str
    title: str
    credits: int
    description: str
    prereqs: List[str]

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/search", response_model=List[CourseSearchResult])
async def search_courses(
    program_id: str = Query(..., description="Program ID to search within"),
    q: str = Query(..., description="Search query (course code or title)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Fuzzy search for courses by code or title

    Args:
        program_id: Program to search within
        q: Search query string
        limit: Maximum results to return

    Returns:
        List of matching courses
    """
    rag_service = RAGService(db)
    courses = rag_service.search_courses(program_id, q, limit)

    return [
        CourseSearchResult(
            code=c.code,
            title=c.title,
            credits=c.credits,
            description=c.description or "",
            prereqs=c.prereqs or []
        )
        for c in courses
    ]
