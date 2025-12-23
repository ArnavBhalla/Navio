"""
Course recommendation API endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.recommend import RecommendRequest, RecommendResponse
from app.services.rag import RAGService
from app.services.ai import AIService
from app.models import Program
from app.core.security import get_current_user, User

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_courses(
    request: RecommendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate course recommendations for next semester

    Args:
        request: RecommendRequest with university, program, completed courses, etc.
        db: Database session

    Returns:
        RecommendResponse with recommendations, notes, assumptions, and warnings
    """

    # Validate program exists
    program = db.query(Program).filter(
        Program.program_id == request.program_id
    ).first()

    if not program:
        raise HTTPException(
            status_code=404,
            detail=f"Program {request.program_id} not found"
        )

    # Initialize services
    rag_service = RAGService(db)
    ai_service = AIService()

    # Retrieve relevant context using RAG
    retrieved = rag_service.retrieve_context(
        program_id=request.program_id,
        completed_courses=request.completed,
        query=f"next semester courses after completing {', '.join(request.completed)}" if request.completed else None
    )

    # Format context for prompt
    context_snippets = rag_service.format_context_snippets(retrieved)

    # Generate recommendations using AI
    result = ai_service.generate_recommendations(
        university=request.university,
        program_id=request.program_id,
        degree=program.degree,
        major=program.major,
        completed=request.completed,
        credits_target=request.credits_target,
        track=request.track,
        preferences=request.preferences,
        context_snippets=context_snippets
    )

    return RecommendResponse(**result)
