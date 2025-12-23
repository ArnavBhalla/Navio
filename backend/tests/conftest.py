"""
Pytest fixtures and configuration for tests
"""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """Get an admin JWT token for testing"""
    response = client.post(
        "/auth/token",
        data={
            "username": settings.DEMO_ADMIN_USERNAME,
            "password": settings.DEMO_ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def user_token(client: TestClient) -> str:
    """Get a regular user JWT token for testing"""
    response = client.post(
        "/auth/token",
        data={
            "username": settings.DEMO_USER_USERNAME,
            "password": settings.DEMO_USER_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Get authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_auth_headers(user_token: str) -> dict:
    """Get authorization headers with user token"""
    return {"Authorization": f"Bearer {user_token}"}

