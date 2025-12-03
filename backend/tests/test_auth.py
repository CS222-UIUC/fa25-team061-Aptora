import os
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.auth.service import AuthService


# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "password": "StrongPassw0rd!",
        "first_name": "Test",
        "last_name": "User"
    }


# ========================
# Registration Tests
# ========================

def test_user_registration_success(client: TestClient, test_user_data):
    """Test successful user registration."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["first_name"] == test_user_data["first_name"]
    assert data["last_name"] == test_user_data["last_name"]
    assert data["is_active"] is True
    assert "hashed_password" not in data  # Password should not be returned


def test_user_registration_duplicate_email(client: TestClient, test_user_data):
    """Test registration with duplicate email fails."""
    # Register first user
    client.post("/auth/register", json=test_user_data)

    # Try to register again with same email
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_user_registration_invalid_email(client: TestClient, test_user_data):
    """Test registration with invalid email fails."""
    test_user_data["email"] = "invalid-email"
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 422  # Validation error


def test_user_registration_short_password(client: TestClient, test_user_data):
    """Test registration with short password fails."""
    test_user_data["password"] = "short"
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 422  # Validation error


# ========================
# Login Tests
# ========================

def test_user_login_success(client: TestClient, test_user_data):
    """Test successful user login."""
    # Register user first
    client.post("/auth/register", json=test_user_data)

    # Login
    login_payload = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_user_login_wrong_password(client: TestClient, test_user_data):
    """Test login with wrong password fails."""
    # Register user first
    client.post("/auth/register", json=test_user_data)

    # Try to login with wrong password
    login_payload = {
        "email": test_user_data["email"],
        "password": "WrongPassword123!"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_user_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user fails."""
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401


# ========================
# Protected Route Tests
# ========================

def test_get_current_user(client: TestClient, test_user_data):
    """Test getting current user information."""
    # Register and login
    client.post("/auth/register", json=test_user_data)
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]


def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token fails."""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token fails."""
    response = client.get("/auth/me")
    assert response.status_code == 403  # No credentials provided


# ========================
# Update User Tests
# ========================

def test_update_user_profile(client: TestClient, test_user_data):
    """Test updating user profile."""
    # Register and login
    client.post("/auth/register", json=test_user_data)
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]

    # Update profile
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    response = client.patch(
        "/auth/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


# ========================
# Password Change Tests
# ========================

def test_change_password_success(client: TestClient, test_user_data):
    """Test successful password change."""
    # Register and login
    client.post("/auth/register", json=test_user_data)
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]

    # Change password
    new_password = "NewStrongPassword123!"
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": test_user_data["password"],
            "new_password": new_password
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Verify new password works
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": new_password
    })
    assert login_response.status_code == 200


def test_change_password_wrong_current(client: TestClient, test_user_data):
    """Test password change with wrong current password fails."""
    # Register and login
    client.post("/auth/register", json=test_user_data)
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]

    # Try to change password with wrong current password
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "WrongPassword!",
            "new_password": "NewPassword123!"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()


# ========================
# Password Reset Tests
# ========================

def test_forgot_password_request(client: TestClient, test_user_data, db_session):
    """Test password reset request."""
    # Register user first
    client.post("/auth/register", json=test_user_data)

    # Request password reset
    response = client.post("/auth/forgot-password", json={
        "email": test_user_data["email"]
    })
    assert response.status_code == 200

    # Verify reset token was created in database
    user = db_session.query(User).filter(User.email == test_user_data["email"]).first()
    assert user.reset_token is not None
    assert user.reset_token_expires is not None


def test_forgot_password_nonexistent_email(client: TestClient):
    """Test password reset for non-existent email (should still return 200)."""
    response = client.post("/auth/forgot-password", json={
        "email": "nonexistent@example.com"
    })
    # Should return 200 to prevent email enumeration
    assert response.status_code == 200


def test_reset_password_with_valid_token(client: TestClient, test_user_data, db_session):
    """Test resetting password with valid token."""
    # Register user
    client.post("/auth/register", json=test_user_data)

    # Request password reset
    client.post("/auth/forgot-password", json={
        "email": test_user_data["email"]
    })

    # Get reset token from database
    user = db_session.query(User).filter(User.email == test_user_data["email"]).first()
    reset_token = user.reset_token

    # Reset password
    new_password = "NewPassword123!"
    response = client.post("/auth/reset-password", json={
        "token": reset_token,
        "new_password": new_password
    })
    assert response.status_code == 200

    # Verify new password works
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": new_password
    })
    assert login_response.status_code == 200


def test_reset_password_with_invalid_token(client: TestClient):
    """Test resetting password with invalid token fails."""
    response = client.post("/auth/reset-password", json={
        "token": "invalid_token",
        "new_password": "NewPassword123!"
    })
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


# ========================
# Email Verification Tests
# ========================

def test_verify_email_with_valid_token(client: TestClient, test_user_data, db_session):
    """Test email verification with valid token."""
    # Register user
    register_response = client.post("/auth/register", json=test_user_data)
    user_id = register_response.json()["id"]

    # Create verification token
    verification_token = AuthService.create_verification_token(db_session, user_id)

    # Verify email
    response = client.get(f"/auth/verify-email/{verification_token}")
    assert response.status_code == 200

    # Verify user is marked as verified
    user = db_session.query(User).filter(User.id == user_id).first()
    assert user.is_verified is True


def test_verify_email_with_invalid_token(client: TestClient):
    """Test email verification with invalid token fails."""
    response = client.get("/auth/verify-email/invalid_token")
    assert response.status_code == 400


# ========================
# Logout Test
# ========================

def test_logout(client: TestClient, test_user_data):
    """Test logout endpoint."""
    # Register and login
    client.post("/auth/register", json=test_user_data)
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]

    # Logout
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()


