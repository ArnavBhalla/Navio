from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RecommendRequest(BaseModel):
    university: str
    program_id: str
    track: Optional[str] = None
    completed: List[str] = Field(default_factory=list)
    credits_target: int = Field(default=15, ge=1, le=21)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class CourseRecommendation(BaseModel):
    code: str
    title: str
    reason: str
    fulfills: List[str]
    prereq_ok: bool
    citations: List[str]


class RecommendResponse(BaseModel):
    recommendations: List[CourseRecommendation]
    notes: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
