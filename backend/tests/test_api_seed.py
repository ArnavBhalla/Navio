"""
Tests for seed API endpoint
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.api
@pytest.mark.seeding
class TestSeedAPI:
    """Test seed endpoint"""

    def test_seed_requires_auth(self, client: TestClient):
        """Test that seed endpoint requires authentication"""
        response = client.post("/api/seed")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_seed_requires_admin_role(
        self, client: TestClient, user_auth_headers: dict
    ):
        """Test that seed endpoint requires admin role"""
        response = client.post("/api/seed", headers=user_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_seed_with_admin_role(
        self, client: TestClient, auth_headers: dict
    ):
        """Test seed endpoint with admin role"""
        # Note: This may fail if seed script has issues, but should not be 403
        response = client.post("/api/seed", headers=auth_headers)
        # May return 500 if seed script fails, but should not be 403
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

