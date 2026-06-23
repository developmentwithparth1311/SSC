"""Engine 4 Step 4.7 — live-server metadata minimization (requires backend on :8000)."""
import os
import uuid

import pytest
import requests

from test_helpers import make_mutual_contacts

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
    return {"X-Forwarded-For": f"10.10.0.{int(SUFFIX, 16) % 200 + 1}"}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_engine4_register_users():
    for tag, lang in (("a", "en"), ("b", "ro")):
        payload = {
            "email": f"e4.{tag}.{SUFFIX}@ssc.dev",
            "password": "E4Pass2026!",
            "username": f"e4{tag}{SUFFIX[:3]}",
            "public_key": f"PK4_{tag}",
            "encrypted_private_key": f"EPK4_{tag}",
            "pk_salt": f"S4_{tag}",
            "language": lang,
            "captcha_token": "TEST-TOKEN",
        }
        r = requests.post(f"{API}/auth/register", json=payload, headers=_reg_headers(), timeout=15)
        assert r.status_code == 200, r.text
        state[f"{tag}_token"] = r.json()["token"]
        state[f"{tag}_user"] = r.json()["user"]


def test_engine4_mutual_contacts():
    make_mutual_contacts(
        API,
        state["a_token"],
        state["b_token"],
        state["b_user"]["username"],
    )


def test_engine4_contacts_expose_online_not_precise_last_seen():
    r = requests.get(f"{API}/contacts", headers=_auth(state["a_token"]), timeout=15)
    assert r.status_code == 200, r.text
    peer = next(c for c in r.json() if c["user_id"] == state["b_user"]["user_id"])
    assert "online" in peer
    if peer.get("online"):
        assert peer.get("last_seen") is None


def test_engine4_conversation_peer_presence_projection():
    r = requests.post(
        f"{API}/conversations",
        json={"peer_username": state["b_user"]["username"]},
        headers=_auth(state["a_token"]),
        timeout=15,
    )
    assert r.status_code == 200, r.text
    conv = r.json()
    peer = conv.get("peer")
    assert peer is not None
    assert "online" in peer
    if peer.get("online"):
        assert peer.get("last_seen") is None