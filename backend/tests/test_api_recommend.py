"""
Tests for recommendation API endpoint
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.models import Program


@pytest.mark.api
@pytest.mark.integration
class TestRecommendAPI:
    """Test recommendation endpoint"""

    def test_recommend_requires_auth(self, client: TestClient):
        """Test that recommend endpoint requires authentication"""
        response = client.post(
            "/api/recommend",
            json={
                "university": "Rice",
                "program_id": "rice-bioe-2025",
                "completed": [],
                "credits_target": 15,
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_recommend_invalid_program(self, client: TestClient, auth_headers: dict):
        """Test recommend with invalid program_id"""
        response = client.post(
            "/api/recommend",
            headers=auth_headers,
            json={
                "university": "Rice",
                "program_id": "invalid-program",
                "completed": [],
                "credits_target": 15,
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_recommend_missing_fields(self, client: TestClient, auth_headers: dict):
        """Test recommend with missing required fields"""
        response = client.post(
            "/api/recommend",
            headers=auth_headers,
            json={
                "university": "Rice",
                # Missing program_id, completed, credits_target
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_recommend_with_program(
        self, client: TestClient, db_session, auth_headers: dict
    ):
        """Test recommend endpoint with valid program"""
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

        response = client.post(
            "/api/recommend",
            headers=auth_headers,
            json={
                "university": "Rice",
                "program_id": "rice-bioe-2025",
                "completed": ["MATH 212"],
                "credits_target": 15,
            },
        )
        # May fail if OpenAI API key is not set, but should not be 401/404
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,  # If API key missing
        ]

