"""Smoke tests for group member routes."""
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


def test_add_group_members_requires_auth():
    r = client.post(
        "/api/conversations/g_test123/members",
        json={"peer_usernames": ["alice"]},
    )
    assert r.status_code == 401