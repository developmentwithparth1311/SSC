"""Smoke tests for POST /api/auth/delete-account."""
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


def test_delete_account_requires_auth():
    r = client.post(
        "/api/auth/delete-account",
        json={"username_confirmation": "someuser"},
    )
    assert r.status_code == 401