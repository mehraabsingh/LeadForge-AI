"""
Tests for authentication endpoints.
"""
import pytest


def test_register_success(client):
    """Test successful user registration."""
    response = client.post("/api/auth/register", json={
        "email": "new.user@test.com",
        "password": "SecurePass@123",
        "first_name": "New",
        "last_name": "User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "new.user@test.com"
    assert data["user"]["role"] == "SALES_REP"
    assert "hashed_password" not in data["user"]


def test_register_duplicate_email(client):
    """Test that duplicate email registration is rejected."""
    payload = {
        "email": "duplicate@test.com",
        "password": "SecurePass@123",
        "first_name": "First",
        "last_name": "User",
    }
    response1 = client.post("/api/auth/register", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/api/auth/register", json=payload)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"].lower()


def test_register_invalid_email(client):
    """Test that invalid email is rejected."""
    response = client.post("/api/auth/register", json={
        "email": "not-an-email",
        "password": "SecurePass@123",
        "first_name": "Test",
        "last_name": "User",
    })
    assert response.status_code == 422


def test_login_success(client, admin_user):
    """Test successful login returns token."""
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@123456",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@test.com"
    assert data["user"]["role"] == "ADMIN"


def test_login_wrong_password(client, admin_user):
    """Test that wrong password is rejected."""
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "WrongPassword123",
    })
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with non-existent email."""
    response = client.post("/api/auth/login", json={
        "email": "ghost@test.com",
        "password": "AnyPass@123",
    })
    assert response.status_code == 401


def test_get_current_user(client, admin_headers):
    """Test /auth/me returns current user profile."""
    response = client.get("/api/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert "hashed_password" not in data


def test_protected_route_without_token(client):
    """Test that protected routes require authentication."""
    response = client.get("/api/leads")
    assert response.status_code == 403


def test_protected_route_with_invalid_token(client):
    """Test that invalid tokens are rejected."""
    response = client.get(
        "/api/leads",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
