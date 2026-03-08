"""
Pytest test suite for ACEest Fitness & Gym Flask API.
Tests converted from Aceestver-3.2.4 logic validation.
"""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as flask_app


@pytest.fixture
def client():
    """Create a test client with an isolated temporary database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    flask_app.app.config["TESTING"] = True
    flask_app.app.config["SECRET_KEY"] = "test-secret"
    flask_app.DB_NAME = db_path

    with flask_app.app.app_context():
        flask_app.init_db()

    with flask_app.app.test_client() as test_client:
        yield test_client

    os.close(db_fd)
    os.unlink(db_path)


# ---------- HEALTH ----------
def test_health_check(client):
    """GET /health should return 200 with healthy status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert "ACEest" in data["app"]


# ---------- AUTH ----------
def test_login_valid_credentials(client):
    """POST /api/login with correct credentials returns 200."""
    resp = client.post("/api/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["user"] == "admin"


def test_login_invalid_credentials(client):
    """POST /api/login with wrong password returns 401."""
    resp = client.post("/api/login", json={"username": "admin", "password": "wrongpass"})
    assert resp.status_code == 401
    assert "error" in resp.get_json()


def test_login_missing_fields(client):
    """POST /api/login without fields returns 400."""
    resp = client.post("/api/login", json={})
    assert resp.status_code == 400


# ---------- CLIENTS ----------
def test_list_clients_empty(client):
    """GET /api/clients on fresh DB returns empty list."""
    resp = client.get("/api/clients")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 0
    assert data["clients"] == []


def test_create_client_valid(client):
    """POST /api/clients with valid data creates client."""
    resp = client.post("/api/clients", json={
        "name": "Arjun",
        "age": 28,
        "weight": 75.0,
        "program": "Fat Loss"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "created"
    assert data["name"] == "Arjun"
    assert data["calories"] == int(75.0 * 22)


def test_create_client_duplicate(client):
    """POST /api/clients with duplicate name returns 409."""
    payload = {"name": "Priya", "weight": 60.0, "program": "Beginner"}
    client.post("/api/clients", json=payload)
    resp = client.post("/api/clients", json=payload)
    assert resp.status_code == 409


def test_create_client_missing_program(client):
    """POST /api/clients without program returns 400."""
    resp = client.post("/api/clients", json={"name": "Rahul", "weight": 80.0})
    assert resp.status_code == 400


def test_create_client_invalid_program(client):
    """POST /api/clients with unknown program returns 400."""
    resp = client.post("/api/clients", json={
        "name": "Test", "weight": 70.0, "program": "InvalidProgram"
    })
    assert resp.status_code == 400


def test_get_client_exists(client):
    """GET /api/clients/<name> returns client data."""
    client.post("/api/clients", json={"name": "Kumar", "weight": 85.0, "program": "Muscle Gain"})
    resp = client.get("/api/clients/Kumar")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Kumar"
    assert data["program"] == "Muscle Gain"


def test_get_client_not_found(client):
    """GET /api/clients/<name> for unknown client returns 404."""
    resp = client.get("/api/clients/NoSuchPerson")
    assert resp.status_code == 404


def test_update_client(client):
    """PUT /api/clients/<name> updates client data."""
    client.post("/api/clients", json={"name": "Deepa", "weight": 65.0, "program": "Beginner"})
    resp = client.put("/api/clients/Deepa", json={"weight": 63.0, "program": "Fat Loss"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["calories"] == int(63.0 * 22)


def test_delete_client(client):
    """DELETE /api/clients/<name> removes client."""
    client.post("/api/clients", json={"name": "Vikram", "weight": 90.0, "program": "Muscle Gain"})
    resp = client.delete("/api/clients/Vikram")
    assert resp.status_code == 200
    assert client.get("/api/clients/Vikram").status_code == 404


# ---------- PROGRAMS ----------
def test_list_programs(client):
    """GET /api/programs returns all 3 programs."""
    resp = client.get("/api/programs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["programs"]) == 3
    assert "Fat Loss" in data["programs"]
    assert "Muscle Gain" in data["programs"]
    assert "Beginner" in data["programs"]


def test_get_program_detail(client):
    """GET /api/programs/<name> returns program details."""
    resp = client.get("/api/programs/Fat Loss")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["factor"] == 22


def test_get_program_not_found(client):
    """GET /api/programs/<name> for unknown program returns 404."""
    resp = client.get("/api/programs/Unknown")
    assert resp.status_code == 404


# ---------- PROGRESS ----------
def test_log_progress_valid(client):
    """POST /api/clients/<name>/progress logs weekly adherence."""
    client.post("/api/clients", json={"name": "Anjali", "weight": 58.0, "program": "Fat Loss"})
    resp = client.post("/api/clients/Anjali/progress", json={"adherence": 85})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["adherence"] == 85


def test_log_progress_invalid_adherence(client):
    """POST progress with adherence > 100 returns 400."""
    client.post("/api/clients", json={"name": "Ravi", "weight": 70.0, "program": "Beginner"})
    resp = client.post("/api/clients/Ravi/progress", json={"adherence": 150})
    assert resp.status_code == 400


def test_get_progress(client):
    """GET /api/clients/<name>/progress returns history."""
    client.post("/api/clients", json={"name": "Meera", "weight": 55.0, "program": "Beginner"})
    client.post("/api/clients/Meera/progress", json={"adherence": 70})
    client.post("/api/clients/Meera/progress", json={"adherence": 80})
    resp = client.get("/api/clients/Meera/progress")
    assert resp.status_code == 200
    assert len(resp.get_json()["progress"]) == 2


# ---------- WORKOUTS ----------
def test_log_workout(client):
    """POST /api/clients/<name>/workouts logs a workout."""
    client.post("/api/clients", json={"name": "Suresh", "weight": 80.0, "program": "Muscle Gain"})
    resp = client.post("/api/clients/Suresh/workouts", json={
        "workout_type": "Strength",
        "duration_min": 60,
        "notes": "Heavy squat day"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["type"] == "Strength"


def test_get_workouts(client):
    """GET /api/clients/<name>/workouts returns workout history."""
    client.post("/api/clients", json={"name": "Lakshmi", "weight": 62.0, "program": "Fat Loss"})
    client.post("/api/clients/Lakshmi/workouts", json={"workout_type": "Cardio", "duration_min": 45})
    resp = client.get("/api/clients/Lakshmi/workouts")
    assert resp.status_code == 200
    assert len(resp.get_json()["workouts"]) == 1


# ---------- MEMBERSHIP ----------
def test_check_membership(client):
    """GET /api/clients/<name>/membership returns membership status."""
    client.post("/api/clients", json={
        "name": "Kavitha", "weight": 68.0, "program": "Beginner",
        "membership_status": "Active", "membership_end": "2025-12-31"
    })
    resp = client.get("/api/clients/Kavitha/membership")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["membership_status"] == "Active"


def test_check_membership_not_found(client):
    """GET membership for unknown client returns 404."""
    resp = client.get("/api/clients/Ghost/membership")
    assert resp.status_code == 404


# ---------- CALORIE CALCULATION (unit test) ----------
def test_calorie_calculation_fat_loss():
    """calculate_calories: 75kg × 22 = 1650 kcal."""
    assert flask_app.calculate_calories(75, "Fat Loss") == 1650


def test_calorie_calculation_muscle_gain():
    """calculate_calories: 80kg × 35 = 2800 kcal."""
    assert flask_app.calculate_calories(80, "Muscle Gain") == 2800


def test_calorie_calculation_beginner():
    """calculate_calories: 60kg × 26 = 1560 kcal."""
    assert flask_app.calculate_calories(60, "Beginner") == 1560
