"""Smoke tests for POST /api/auth/change-password."""
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


def test_change_password_requires_auth():
    r = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "oldpass123",
            "new_password": "newpass123",
            "encrypted_private_key": "x" * 32,
            "pk_salt": "c2FsdA==",
        },
    )
    assert r.status_code == 401