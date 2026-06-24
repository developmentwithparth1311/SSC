"""Engine 8.6 — migration / dual-read policy tests."""
from core.migration_policy import (
    DUAL_READ_PROTOCOLS,
    dual_read_active,
    is_legacy_protocol,
    is_signal_protocol,
    normalize_message_protocol,
)


def test_dual_read_protocols():
    assert DUAL_READ_PROTOCOLS == frozenset({
        "legacy_rsa", "signal_v1", "signal_group_v1", "signal_status_v1",
    })


def test_normalize_defaults_to_legacy():
    assert normalize_message_protocol(None) == "legacy_rsa"
    assert normalize_message_protocol("") == "legacy_rsa"
    assert normalize_message_protocol("signal_v1") == "signal_v1"


def test_normalize_unknown_to_legacy():
    assert normalize_message_protocol("unknown") == "legacy_rsa"


def test_dual_read_active():
    assert dual_read_active() is True


def test_protocol_helpers():
    assert is_legacy_protocol(None) is True
    assert is_signal_protocol("signal_v1") is True
    assert is_signal_protocol("legacy_rsa") is False