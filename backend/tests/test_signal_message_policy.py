"""Engine 8.5 — signal_v1 message policy tests."""
import base64

import pytest

from core.signal_message_policy import (
    SignalMessageValidationError,
    validate_send_payload,
    validate_signal_ciphertext,
)
from core.signal_policy import ProtocolVersion


def _cipher_b64(n: int = 64) -> str:
    return base64.b64encode(b"x" * n).decode()


def test_signal_v1_payload_ok():
    out = validate_send_payload(
        protocol="signal_v1",
        ciphertext=_cipher_b64(),
        iv=None,
        encrypted_keys=None,
        signal_message_type=3,
        is_group=False,
        participant_ids=["a", "b"],
    )
    assert out["protocol"] == ProtocolVersion.SIGNAL_V1.value
    assert out["encrypted_keys"] is None
    assert out["signal_message_type"] == 3


def test_signal_v1_rejects_group():
    with pytest.raises(SignalMessageValidationError, match="1:1"):
        validate_send_payload(
            protocol="signal_v1",
            ciphertext=_cipher_b64(),
            iv=None,
            encrypted_keys=None,
            signal_message_type=2,
            is_group=True,
            participant_ids=["a", "b", "c"],
        )


def test_signal_v1_rejects_encrypted_keys():
    with pytest.raises(SignalMessageValidationError, match="encrypted_keys"):
        validate_send_payload(
            protocol="signal_v1",
            ciphertext=_cipher_b64(),
            iv=None,
            encrypted_keys={"a": "k"},
            signal_message_type=2,
            is_group=False,
            participant_ids=["a", "b"],
        )


def test_legacy_requires_keys():
    with pytest.raises(SignalMessageValidationError, match="encrypted_keys"):
        validate_send_payload(
            protocol="legacy_rsa",
            ciphertext="ct",
            iv="iv",
            encrypted_keys=None,
            signal_message_type=None,
            is_group=False,
            participant_ids=["a", "b"],
        )


def test_validate_signal_ciphertext_bounds():
    with pytest.raises(SignalMessageValidationError):
        validate_signal_ciphertext("!!!")