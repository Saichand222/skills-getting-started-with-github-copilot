import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    # Backup activities state and restore after each test to keep tests isolated
    backup = copy.deepcopy(activities)
    with TestClient(app) as c:
        yield c
    activities.clear()
    activities.update(backup)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    participants = data["Chess Club"]["participants"]
    assert "michael@mergington.edu" in participants
    assert "daniel@mergington.edu" in participants


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    new_email = "pytestuser@mergington.edu"

    # Signup should succeed
    signup_resp = client.post(f"/activities/{activity}/signup?email={new_email}")
    assert signup_resp.status_code == 200
    assert f"Signed up {new_email}" in signup_resp.json().get("message", "")

    # Now the participant should be present
    get_resp = client.get("/activities")
    assert get_resp.status_code == 200
    assert new_email in get_resp.json()[activity]["participants"]

    # Unregister should succeed
    unregister_resp = client.delete(f"/activities/{activity}/unregister?email={new_email}")
    assert unregister_resp.status_code == 200
    assert f"Unregistered {new_email}" in unregister_resp.json().get("message", "")

    # Participant should no longer be present
    final = client.get("/activities").json()
    assert new_email not in final[activity]["participants"]


def test_signup_already_registered(client):
    activity = "Chess Club"
    existing = "michael@mergington.edu"

    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_nonexistent(client):
    activity = "Chess Club"
    fake = "noone@mergington.edu"

    resp = client.delete(f"/activities/{activity}/unregister?email={fake}")
    assert resp.status_code == 404
