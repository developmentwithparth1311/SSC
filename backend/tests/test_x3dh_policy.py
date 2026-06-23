"""Engine 8.4 — X3DH session policy tests."""
import pytest

from core.x3dh_policy import (
    FORBIDDEN_SESSION_SERVER_FIELDS,
    X3DH_CLIENT_REQUIREMENTS,
    X3DH_SERVER_REQUIREMENTS,
    validate_no_session_fields_on_server,
    x3dh_session_server_allowed,
)


def test_server_never_persists_sessions():
    assert x3dh_session_server_allowed() is False


def test_forbidden_session_fields():
    assert "session_record" in FORBIDDEN_SESSION_SERVER_FIELDS
    assert "ratchet_state" in FORBIDDEN_SESSION_SERVER_FIELDS


def test_validate_no_session_fields_raises():
    with pytest.raises(ValueError, match="forbidden session fields"):
        validate_no_session_fields_on_server({"session_record": "x"})


def test_x3dh_requirements_documented():
    assert len(X3DH_CLIENT_REQUIREMENTS) >= 3
    assert len(X3DH_SERVER_REQUIREMENTS) >= 2
    assert "never_store_session_records" in X3DH_SERVER_REQUIREMENTS


def test_consume_one_time_prekey():
    from core.prekey_bundle import consume_one_time_prekey

    doc = {"one_time_prekeys": [{"prekey_id": 1, "public": "a"}, {"prekey_id": 2, "public": "b"}]}
    patch, consumed = consume_one_time_prekey(doc)
    assert consumed["prekey_id"] == 1
    assert len(patch["one_time_prekeys"]) == 1