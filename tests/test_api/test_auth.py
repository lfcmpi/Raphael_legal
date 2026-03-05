"""Tests for authentication endpoints."""

from tests.test_api.conftest import TEST_EMAIL, TEST_PASSWORD


def test_login_success(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": TEST_EMAIL, "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "test"})
    assert resp.status_code == 401


def test_protected_endpoint_without_token(client):
    resp = client.get("/api/cases")
    assert resp.status_code == 401


def test_protected_endpoint_with_invalid_token(client):
    resp = client.get("/api/cases", headers={"Authorization": "Bearer invalid-token"})
    assert resp.status_code == 401
