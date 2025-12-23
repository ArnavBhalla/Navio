"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.auth
@pytest.mark.api
class TestAuth:
    """Test authentication endpoints"""

    def test_login_success_admin(self, client: TestClient):
        """Test successful admin login"""
        response = client.post(
            "/auth/token",
            data={
                "username": "admin",
                "password": "admin123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_success_user(self, client: TestClient):
        """Test successful regular user login"""
        response = client.post(
            "/auth/token",
            data={
                "username": "demo",
                "password": "demo123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client: TestClient):
        """Test login with invalid username"""
        response = client.post(
            "/auth/token",
            data={
                "username": "invalid_user",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient):
        """Test login with invalid password"""
        response = client.post(
            "/auth/token",
            data={
                "username": "admin",
                "password": "wrong_password",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials"""
        response = client.post("/auth/token", data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

