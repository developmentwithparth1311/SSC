"""Engine 4 Steps 4.4–4.5 — generic push payloads."""
from core.metadata_policy import GENERIC_PUSH_BODY, GENERIC_PUSH_TITLE
from core.push_payload import (
    ACTIVITY_CALL,
    ACTIVITY_MESSAGE,
    build_generic_push,
    sanitize_push_data,
)


def test_build_generic_push_message():
    payload = build_generic_push(ACTIVITY_MESSAGE, conversation_id="c_abc", tag="c_abc")
    assert payload["title"] == GENERIC_PUSH_TITLE
    assert payload["body"] == GENERIC_PUSH_BODY
    assert payload["data"]["type"] == ACTIVITY_MESSAGE
    assert payload["data"]["conversation_id"] == "c_abc"
    assert "username" not in str(payload).lower() or "ssc" in payload["title"].lower()


def test_build_generic_push_call_no_username():
    payload = build_generic_push(
        ACTIVITY_CALL,
        conversation_id="c_call",
        extra_data={"from": "u_x", "mode": "audio", "group": False},
    )
    assert payload["title"] == GENERIC_PUSH_TITLE
    assert payload["body"] == GENERIC_PUSH_BODY
    assert "@" not in payload["body"]
    assert payload["data"]["mode"] == "audio"


def test_sanitize_push_data_strips_forbidden_keys():
    raw = {
        "type": "status",
        "conversation_id": "c_1",
        "author_username": "alice",
        "group_name": "Secret Group",
        "from": "u_a",
    }
    out = sanitize_push_data(raw)
    assert "author_username" not in out
    assert "group_name" not in out
    assert out["from"] == "u_a"
    assert out["type"] == "status"