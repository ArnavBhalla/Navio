"""
RAG service for retrieval and context generation
"""
from typing import List, Dict, Any
import math
from sqlalchemy.orm import Session
from openai import OpenAI
from app.core.config import settings
from app.models import Embedding, Course, Requirement


class RAGService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text"""
        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def cosine_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine distance (1 - similarity)"""
        return 1.0 - self.cosine_similarity(vec1, vec2)

    def retrieve_context(
        self,
        program_id: str,
        completed_courses: List[str],
        query: str = None,
        k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using vector similarity search

        Args:
            program_id: Filter by program
            completed_courses: List of completed course codes (for re-ranking)
            query: Optional query text (if None, uses generic query)
            k: Number of results to return (default from settings)
        """
        if k is None:
            k = settings.RETRIEVAL_K

        # Create query
        if query is None:
            query = f"course recommendations and requirements for {program_id}"

        # Generate query embedding
        query_vector = self.generate_embedding(query)

        # Fetch all embeddings for the program
        embeddings = self.db.query(Embedding).filter(
            Embedding.program_id == program_id
        ).all()

        # Calculate cosine distance for each embedding
        retrieved = []
        for emb in embeddings:
            distance = self.cosine_distance(query_vector, emb.vector)
            retrieved.append({
                "id": emb.id,
                "program_id": emb.program_id,
                "type": emb.type,
                "content_text": emb.content_text,
                "metadata": emb.meta_data,
                "distance": distance
            })

        # Sort by distance (lower is better)
        retrieved.sort(key=lambda x: x["distance"])
        
        # Take top k * 2 for re-ranking
        retrieved = retrieved[:k * 2]

        # Re-rank based on prerequisite matches
        retrieved = self._rerank_by_prereqs(retrieved, completed_courses)

        # Return top k after re-ranking
        return retrieved[:k]

    def _rerank_by_prereqs(
        self,
        results: List[Dict[str, Any]],
        completed_courses: List[str]
    ) -> List[Dict[str, Any]]:
        """Re-rank results by exact course code matches"""
        if not completed_courses:
            return results

        # Boost score for courses that have prerequisites in completed list
        for result in results:
            boost = 0
            content = result["content_text"].lower()

            # Check for exact course code matches
            for completed in completed_courses:
                if completed.lower() in content:
                    boost += 0.1  # Reduce distance (better ranking)

            result["distance"] = max(0, result["distance"] - boost)

        # Re-sort by adjusted distance
        results.sort(key=lambda x: x["distance"])
        return results

    def get_course_by_code(self, program_id: str, code: str) -> Course:
        """Get course by code"""
        return self.db.query(Course).filter(
            Course.program_id == program_id,
            Course.code == code
        ).first()

    def search_courses(
        self,
        program_id: str,
        query: str,
        limit: int = 10
    ) -> List[Course]:
        """Fuzzy search for courses"""
        return self.db.query(Course).filter(
            Course.program_id == program_id,
            (Course.code.ilike(f"%{query}%") | Course.title.ilike(f"%{query}%"))
        ).limit(limit).all()

    def format_context_snippets(
        self,
        retrieved: List[Dict[str, Any]]
    ) -> List[str]:
        """Format retrieved items as text snippets for the prompt"""
        snippets = []
        for item in retrieved:
            snippets.append(item["content_text"])
        return snippets
