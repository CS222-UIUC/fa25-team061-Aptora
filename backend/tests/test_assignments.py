import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

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
    client.post(
        "/auth/register/",
        json={
            "email": "student@example.com",
            "password": "StrongPassw0rd!",
            "first_name": "Study",
            "last_name": "User",
        },
    )
    response = client.post(
        "/auth/jwt/login",
        data={"username": "student@example.com", "password": "StrongPassw0rd!"},
    )
    return response.json()["access_token"]


def create_course(client: TestClient, headers: dict) -> int:
    course_payload = {"name": "Algorithms", "code": "CS-374", "description": "Test"}
    response = client.post("/courses/", json=course_payload, headers=headers)
    assert response.status_code in (200, 201), response.text
    return response.json()["id"]


def future_date(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def test_assignment_crud_and_filters(client: TestClient):
    token = auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    course_id = create_course(client, headers)

    payload = {
        "title": "Midterm Review",
        "description": "Prepare for midterm",
        "due_date": future_date(5),
        "estimated_hours": 3.0,
        "difficulty": "medium",
        "task_type": "exam",
        "priority": "high",
        "course_id": course_id,
    }
    response = client.post("/assignments/", json=payload, headers=headers)
    assert response.status_code in (200, 201), response.text
    assignment = response.json()
    assignment_id = assignment["id"]
    assert assignment["priority"] == "high"
    assert not assignment["is_completed"]

    list_response = client.get("/assignments/", headers=headers)
    assert list_response.status_code == 200
    assignments = list_response.json()
    assert any(item["id"] == assignment_id for item in assignments)

    filter_response = client.get(
        "/assignments/",
        headers=headers,
        params={"priority": "high", "course_id": course_id},
    )
    assert filter_response.status_code == 200
    filtered = filter_response.json()
    assert len(filtered) == 1
    assert filtered[0]["id"] == assignment_id

    due_filter_response = client.get(
        "/assignments/",
        headers=headers,
        params={"due_before": future_date(10), "due_after": future_date(1)},
    )
    assert due_filter_response.status_code == 200
    assert any(item["id"] == assignment_id for item in due_filter_response.json())

    update_payload = {
        "title": "Midterm Review Session",
        "due_date": future_date(7),
        "priority": "medium",
    }
    update_response = client.put(
        f"/assignments/{assignment_id}", json=update_payload, headers=headers
    )
    assert update_response.status_code == 200
    updated_assignment = update_response.json()
    assert updated_assignment["title"] == update_payload["title"]
    assert updated_assignment["priority"] == "medium"

    complete_response = client.patch(
        f"/assignments/{assignment_id}/complete", headers=headers
    )
    assert complete_response.status_code == 200
    completed_assignment = complete_response.json()
    assert completed_assignment["is_completed"] is True

    delete_response = client.delete(
        f"/assignments/{assignment_id}", headers=headers
    )
    assert delete_response.status_code == 200

    fetch_deleted = client.get(
        f"/assignments/{assignment_id}", headers=headers
    )
    assert fetch_deleted.status_code == 404


def test_assignment_due_date_validation(client: TestClient):
    token = auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    course_id = create_course(client, headers)

    past_payload = {
        "title": "Past Task",
        "description": "Already due",
        "due_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "estimated_hours": 1.0,
        "difficulty": "easy",
        "task_type": "assignment",
        "priority": "low",
        "course_id": course_id,
    }
    response = client.post("/assignments/", json=past_payload, headers=headers)
    assert response.status_code == 422

