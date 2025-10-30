import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


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


def auth_token(client: TestClient) -> str:
    # Register and login to get token
    client.post(
        "/auth/register/",
        json={
            "email": "c@example.com",
            "password": "StrongPassw0rd!",
            "first_name": "C",
            "last_name": "User",
        },
    )
    r = client.post(
        "/auth/jwt/login",
        data={"username": "c@example.com", "password": "StrongPassw0rd!"},
    )
    token = r.json()["access_token"]
    return token


def test_course_crud_flow(client: TestClient):
    token = auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create course
    payload = {"name": "Algebra", "code": "MATH-101", "description": "Intro"}
    r = client.post("/courses/", json=payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    course = r.json()
    course_id = course["id"]
    assert course["name"] == payload["name"]

    # List courses
    r = client.get("/courses/", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert any(c["id"] == course_id for c in items)

    # Update course
    r = client.put(
        f"/courses/{course_id}",
        json={"description": "Updated"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["description"] == "Updated"

    # Delete course
    r = client.delete(f"/courses/{course_id}", headers=headers)
    assert r.status_code == 200

    # Ensure it's gone
    r = client.get(f"/courses/{course_id}", headers=headers)
    assert r.status_code == 404


