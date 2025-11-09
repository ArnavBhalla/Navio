"""
RAG service for retrieval and context generation
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
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

        # Perform vector similarity search with pgvector
        # Using cosine distance operator <=>
        sql = text("""
            SELECT
                id,
                program_id,
                type,
                content_text,
                metadata,
                vector <=> CAST(:query_vector AS vector) AS distance
            FROM embeddings
            WHERE program_id = :program_id
            ORDER BY vector <=> CAST(:query_vector AS vector)
            LIMIT :k
        """)

        results = self.db.execute(
            sql,
            {
                "query_vector": str(query_vector),
                "program_id": program_id,
                "k": k * 2  # Get more for re-ranking
            }
        ).fetchall()

        # Convert to list of dicts
        retrieved = []
        for row in results:
            retrieved.append({
                "id": row.id,
                "program_id": row.program_id,
                "type": row.type,
                "content_text": row.content_text,
                "metadata": row.metadata,
                "distance": row.distance
            })

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
