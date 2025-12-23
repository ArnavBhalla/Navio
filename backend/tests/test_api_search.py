"""
Tests for search API endpoint
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.models import Program, Course


@pytest.mark.api
@pytest.mark.integration
class TestSearchAPI:
    """Test search endpoint"""

    def test_search_requires_auth(self, client: TestClient):
        """Test that search endpoint requires authentication"""
        response = client.get("/api/search?program_id=test&q=test")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_missing_params(self, client: TestClient, auth_headers: dict):
        """Test search with missing query parameters"""
        response = client.get("/api/search", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_empty_results(
        self, client: TestClient, db_session, auth_headers: dict
    ):
        """Test search with no matching courses"""
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
        db_session.commit()

        response = client.get(
            "/api/search?program_id=rice-bioe-2025&q=NONEXISTENT",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_search_with_results(
        self, client: TestClient, db_session, auth_headers: dict
    ):
        """Test search with matching courses"""
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

        # Create a test course
        course = Course(
            program_id="rice-bioe-2025",
            code="BIOE 252",
            title="Introduction to Bioengineering",
            credits=3,
            description="Intro course",
            prereqs=[],
            terms=["Fall", "Spring"],
            tags=[],
            source_url="https://example.com",
        )
        db_session.add(course)
        db_session.commit()

        response = client.get(
            "/api/search?program_id=rice-bioe-2025&q=BIOE",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results) > 0
        assert results[0]["code"] == "BIOE 252"

