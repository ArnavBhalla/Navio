"""
Tests for health check and metrics endpoints
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.api
@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check_success(self, client: TestClient, db_session):
        """Test main health check endpoint with database"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] == "healthy"

    def test_liveness_check(self, client: TestClient):
        """Test Kubernetes liveness probe"""
        response = client.get("/health/live")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "alive"
        assert "timestamp" in data

    def test_readiness_check(self, client: TestClient, db_session):
        """Test Kubernetes readiness probe"""
        response = client.get("/health/ready")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "ready"
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["database"] == "ready"


@pytest.mark.api
@pytest.mark.integration
class TestMetricsEndpoint:
    """Test metrics endpoint"""

    def test_metrics_endpoint(self, client: TestClient, db_session):
        """Test metrics endpoint returns system and database stats"""
        response = client.get("/metrics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check basic fields
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0

        # Check system metrics
        assert "system" in data
        assert "cpu_percent" in data["system"]
        assert "memory" in data["system"]
        assert "disk" in data["system"]

        # Check memory stats
        memory = data["system"]["memory"]
        assert "total_gb" in memory
        assert "available_gb" in memory
        assert "used_percent" in memory

        # Check disk stats
        disk = data["system"]["disk"]
        assert "total_gb" in disk
        assert "free_gb" in disk
        assert "used_percent" in disk

        # Check database stats
        assert "database" in data
        # Database should be empty in test environment
        if "error" not in data["database"]:
            assert "programs" in data["database"]
            assert "courses" in data["database"]
            assert "requirements" in data["database"]
            assert "embeddings" in data["database"]


@pytest.mark.api
class TestRequestIDMiddleware:
    """Test request ID middleware"""

    def test_request_id_added_to_response(self, client: TestClient):
        """Test that request ID is added to response headers"""
        response = client.get("/")

        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0

    def test_custom_request_id_preserved(self, client: TestClient):
        """Test that custom request ID from headers is preserved"""
        custom_id = "custom-test-request-id"
        response = client.get("/", headers={"X-Request-ID": custom_id})

        assert response.headers["X-Request-ID"] == custom_id

    def test_request_id_unique_per_request(self, client: TestClient):
        """Test that each request gets a unique ID"""
        response1 = client.get("/")
        response2 = client.get("/")

        id1 = response1.headers["X-Request-ID"]
        id2 = response2.headers["X-Request-ID"]

        assert id1 != id2


@pytest.mark.api
class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["message"] == "Navio Academic Advisor API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
        assert data["metrics"] == "/metrics"
