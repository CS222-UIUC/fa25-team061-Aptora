import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
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
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_user_registration_and_login_flow(client: TestClient):
    # Register
    register_payload = {
        "email": "test@example.com",
        "password": "StrongPassw0rd!",
        "first_name": "Test",
        "last_name": "User"
    }
    r = client.post("/auth/register/", json=register_payload)
    assert r.status_code in (200, 201), r.text

    # Login
    login_payload = {
        "username": register_payload["email"],
        "password": register_payload["password"]
    }
    r = client.post("/auth/jwt/login", data=login_payload)
    assert r.status_code == 200, r.text
    token = r.json().get("access_token")
    assert token

    # /auth/me with token
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    me = r.json()
    assert me["email"] == register_payload["email"]


