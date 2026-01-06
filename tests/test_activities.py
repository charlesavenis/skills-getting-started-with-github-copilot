import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # keep original state and restore after each test to avoid cross-test pollution
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_prevent_duplicates():
    activity = "Art Club"
    email = "testuser@example.com"

    # ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # signup should succeed
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup should fail
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400


def test_unregister():
    activity = "Math Club"
    email = "unregister@example.com"

    # ensure participant present
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    r = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r.status_code == 200
    assert email not in activities[activity]["participants"]

    # deleting again should return 404
    r2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r2.status_code == 404


def test_signup_invalid_activity():
    r = client.post("/activities/Nope/signup", params={"email": "a@b.com"})
    assert r.status_code == 404


def test_unregister_invalid_activity():
    r = client.delete("/activities/Nope/participants", params={"email": "a@b.com"})
    assert r.status_code == 404
