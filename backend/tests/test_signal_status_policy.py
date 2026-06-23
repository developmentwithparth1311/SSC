"""Engine 8.12 — signal_status_v1 stories policy tests."""
import base64

import pytest

from core.signal_message_policy import SignalMessageValidationError
from core.signal_policy import ProtocolVersion
from core.signal_status_policy import validate_status_payload


def _cipher_b64(n: int = 64) -> str:
    return base64.b64encode(b"x" * n).decode()


def test_signal_status_v1_payload_ok():
    out = validate_status_payload(
        protocol="signal_status_v1",
        ciphertext=_cipher_b64(),
        iv=None,
        encrypted_keys=None,
        signal_message_type=7,
        distribution_id="550e8400-e29b-41d4-a716-446655440000",
        author_id="u_author",
    )
    assert out["protocol"] == ProtocolVersion.SIGNAL_STATUS_V1.value
    assert out["signal_message_type"] == 7
    assert out["encrypted_keys"] is None


def test_signal_status_v1_rejects_rsa_fields():
    with pytest.raises(SignalMessageValidationError, match="encrypted_keys"):
        validate_status_payload(
            protocol="signal_status_v1",
            ciphertext=_cipher_b64(),
            iv=None,
            encrypted_keys={"u_a": "k"},
            signal_message_type=7,
            distribution_id="550e8400-e29b-41d4-a716-446655440000",
            author_id="u_author",
        )


def test_legacy_status_requires_keys():
    with pytest.raises(SignalMessageValidationError, match="encrypted_keys"):
        validate_status_payload(
            protocol="legacy_rsa",
            ciphertext="ct",
            iv="iv",
            encrypted_keys=None,
            signal_message_type=None,
            distribution_id=None,
            author_id="u_author",
        )