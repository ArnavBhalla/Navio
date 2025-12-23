"""
Tests for RAG service
"""
import pytest
from app.services.rag import RAGService
from app.models import Embedding, Program, Course


@pytest.mark.rag
@pytest.mark.unit
class TestRAGService:
    """Test RAG service functionality"""

    def test_cosine_similarity_identical_vectors(self, db_session):
        """Test cosine similarity with identical vectors"""
        service = RAGService(db_session)
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = service.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001

    def test_cosine_similarity_orthogonal_vectors(self, db_session):
        """Test cosine similarity with orthogonal vectors"""
        service = RAGService(db_session)
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        similarity = service.cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 0.001

    def test_cosine_distance(self, db_session):
        """Test cosine distance calculation"""
        service = RAGService(db_session)
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        distance = service.cosine_distance(vec1, vec2)
        assert abs(distance - 0.0) < 0.001

    def test_cosine_similarity_different_lengths(self, db_session):
        """Test cosine similarity with vectors of different lengths"""
        service = RAGService(db_session)
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = service.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_retrieve_context_empty_database(self, db_session):
        """Test retrieve_context with empty database"""
        service = RAGService(db_session)
        results = service.retrieve_context(
            program_id="test-program",
            completed_courses=[],
            query="test query",
        )
        assert results == []

    def test_retrieve_context_with_embeddings(
        self, db_session
    ):
        """Test retrieve_context with embeddings in database"""
        # Create a test program
        program = Program(
            program_id="rice-bioe-2025",
            university="Rice",
            degree="BS",
            major="Bioengineering",
            catalog_url="https://example.com",
            version_year=2025,
        )
        db_session.add(program)
        db_session.flush()

        # Create a test embedding
        test_vector = [0.1] * 1536  # Mock embedding vector
        embedding = Embedding(
            program_id="rice-bioe-2025",
            type="course",
            content_text="Test course content",
            vector=test_vector,
            meta_data={"code": "TEST 101"},
        )
        db_session.add(embedding)
        db_session.commit()

        service = RAGService(db_session)
        results = service.retrieve_context(
            program_id="rice-bioe-2025",
            completed_courses=[],
            query="test query",
        )
        assert len(results) > 0
        assert results[0]["program_id"] == "rice-bioe-2025"
        assert "distance" in results[0]

    def test_search_courses(self, db_session):
        """Test search_courses method"""
        # Create a test program
        program = Program(
            program_id="rice-bioe-2025",
            university="Rice",
            degree="BS",
            major="Bioengineering",
            catalog_url="https://example.com",
            version_year=2025,
        )
        db_session.add(program)
        db_session.flush()

        # Create test courses
        course1 = Course(
            program_id="rice-bioe-2025",
            code="BIOE 252",
            title="Introduction to Bioengineering",
            credits=3,
            description="Intro course",
            prereqs=[],
            terms=["Fall"],
            tags=[],
            source_url="https://example.com",
        )
        course2 = Course(
            program_id="rice-bioe-2025",
            code="BIOE 310",
            title="Biomechanics",
            credits=3,
            description="Biomechanics course",
            prereqs=["BIOE 252"],
            terms=["Spring"],
            tags=[],
            source_url="https://example.com",
        )
        db_session.add_all([course1, course2])
        db_session.commit()

        service = RAGService(db_session)
        results = service.search_courses("rice-bioe-2025", "BIOE", limit=10)
        assert len(results) == 2
        assert all(c.code.startswith("BIOE") for c in results)

