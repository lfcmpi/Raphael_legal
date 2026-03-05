"""Shared fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.auth import hash_password
from api.database import get_db
from api.db_models import Base, User
from api.main import app

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"


@pytest.fixture()
def db_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Create a DB session from the test engine."""
    TestSession = sessionmaker(bind=db_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """TestClient with overridden DB dependency."""
    def _override_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session):
    """Create admin user in test DB."""
    user = User(
        email=TEST_EMAIL,
        hashed_password=hash_password(TEST_PASSWORD),
        nome="Test Admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(client, admin_user):
    """Get auth headers with valid JWT token."""
    resp = client.post("/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
