"""Engine 5 Step 5.7 — live-server session hardening (requires backend on :8000)."""
import os
import uuid

import pytest
import requests

from core.session_cookie import session_cookie_max_age
from core.session_policy import SESSION_COOKIE_NAME

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8000").rstrip("/")
API = f"{BASE_URL}/api"
SUFFIX = uuid.uuid4().hex[:4]


def _server_up() -> bool:
    try:
        r = requests.get(f"{API}/", timeout=3)
        return r.status_code == 200 and r.json().get("status") == "ok"
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _server_up(), reason="backend not running on :8000")

state: dict = {}


def _reg_headers():
    return {"X-Forwarded-For": f"10.20.0.{int(SUFFIX, 16) % 200 + 1}"}


def test_engine5_register_sets_httponly_session_cookie():
    state["session"] = requests.Session()
    payload = {
        "email": f"e5.{SUFFIX}@ssc.dev",
        "password": "E5Pass2026!",
        "username": f"e5{SUFFIX[:5]}",
        "public_key": "PK5",
        "encrypted_private_key": "EPK5",
        "pk_salt": "S5",
        "language": "en",
        "captcha_token": "TEST-TOKEN",
    }
    r = state["session"].post(
        f"{API}/auth/register", json=payload, headers=_reg_headers(), timeout=15,
    )
    assert r.status_code == 200, r.text
    state["token"] = r.json()["token"]
    state["user"] = r.json()["user"]
    cookie_header = r.headers.get("set-cookie", "")
    assert SESSION_COOKIE_NAME in cookie_header
    assert "HttpOnly" in cookie_header
    assert f"Max-Age={session_cookie_max_age()}" in cookie_header


def test_engine5_auth_me_via_cookie_without_bearer():
    r = state["session"].get(f"{API}/auth/me", timeout=15)
    assert r.status_code == 200, r.text
    assert r.json()["user_id"] == state["user"]["user_id"]


def test_engine5_logout_clears_cookie_and_revokes_session():
    r = state["session"].post(f"{API}/auth/logout", timeout=15)
    assert r.status_code == 200, r.text
    clear_header = r.headers.get("set-cookie", "")
    assert SESSION_COOKIE_NAME in clear_header
    assert "Max-Age=0" in clear_header or '=""' in clear_header

    r_me = state["session"].get(f"{API}/auth/me", timeout=15)
    assert r_me.status_code == 401

    r_bearer = requests.get(
        f"{API}/auth/me",
        headers={"Authorization": f"Bearer {state['token']}"},
        timeout=15,
    )
    assert r_bearer.status_code == 401


def test_engine5_login_sets_cookie_for_existing_user():
    payload = {
        "email": f"e5.{SUFFIX}@ssc.dev",
        "password": "E5Pass2026!",
        "captcha_token": "TEST-TOKEN",
    }
    r = requests.post(f"{API}/auth/login", json=payload, headers=_reg_headers(), timeout=15)
    assert r.status_code == 200, r.text
    cookie_header = r.headers.get("set-cookie", "")
    assert SESSION_COOKIE_NAME in cookie_header
    assert "HttpOnly" in cookie_header