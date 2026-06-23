"""Signal Protocol message policy — Engine 8.5 (signal_v1 ciphertext relay)."""
from __future__ import annotations

import base64
import re
from typing import Any, Dict, Optional

from core.signal_policy import ProtocolVersion

_B64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
MAX_SIGNAL_CIPHERTEXT_B64 = 512_000
MIN_SIGNAL_CIPHERTEXT_BYTES = 16
MAX_SIGNAL_CIPHERTEXT_BYTES = 384_000

# libsignal CiphertextMessage types (WHISPER=2, PREKEY=3)
ALLOWED_SIGNAL_MESSAGE_TYPES = frozenset({2, 3})


class SignalMessageValidationError(ValueError):
    pass


def normalize_protocol(value: Optional[str]) -> str:
    raw = (value or ProtocolVersion.LEGACY_RSA.value).strip().lower()
    if raw not in (ProtocolVersion.LEGACY_RSA.value, ProtocolVersion.SIGNAL_V1.value):
        raise SignalMessageValidationError(f"unsupported protocol: {raw}")
    return raw


def validate_signal_ciphertext(b64_value: str) -> str:
    if not b64_value or not isinstance(b64_value, str):
        raise SignalMessageValidationError("ciphertext required")
    raw = b64_value.strip()
    if len(raw) > MAX_SIGNAL_CIPHERTEXT_B64 or not _B64_RE.match(raw):
        raise SignalMessageValidationError("ciphertext invalid base64")
    try:
        data = base64.b64decode(raw, validate=True)
    except Exception as exc:
        raise SignalMessageValidationError("ciphertext invalid base64") from exc
    if not (MIN_SIGNAL_CIPHERTEXT_BYTES <= len(data) <= MAX_SIGNAL_CIPHERTEXT_BYTES):
        raise SignalMessageValidationError("ciphertext invalid length")
    return raw


def validate_signal_message_type(value: Optional[int]) -> int:
    if not isinstance(value, int) or value not in ALLOWED_SIGNAL_MESSAGE_TYPES:
        raise SignalMessageValidationError("signal_message_type must be 2 (whisper) or 3 (prekey)")
    return value


def validate_send_payload(
    *,
    protocol: str,
    ciphertext: str,
    iv: Optional[str],
    encrypted_keys: Optional[Dict[str, Any]],
    signal_message_type: Optional[int],
    is_group: bool,
    participant_ids: list[str],
) -> Dict[str, Any]:
    """Return normalized storage fields for a new message."""
    proto = normalize_protocol(protocol)
    if proto == ProtocolVersion.SIGNAL_V1.value:
        if is_group:
            raise SignalMessageValidationError("signal_v1 is 1:1 direct only")
        if len(participant_ids) != 2:
            raise SignalMessageValidationError("signal_v1 requires a 1:1 conversation")
        if iv:
            raise SignalMessageValidationError("iv not allowed for signal_v1")
        if encrypted_keys:
            raise SignalMessageValidationError("encrypted_keys not allowed for signal_v1")
        return {
            "protocol": ProtocolVersion.SIGNAL_V1.value,
            "ciphertext": validate_signal_ciphertext(ciphertext),
            "signal_message_type": validate_signal_message_type(signal_message_type),
            "iv": None,
            "encrypted_keys": None,
        }

    if not iv:
        raise SignalMessageValidationError("iv required for legacy_rsa")
    if not encrypted_keys:
        raise SignalMessageValidationError("encrypted_keys required for legacy_rsa")
    missing = [uid for uid in participant_ids if uid not in encrypted_keys]
    if missing:
        raise SignalMessageValidationError(f"encrypted_keys missing for: {','.join(missing)}")
    return {
        "protocol": ProtocolVersion.LEGACY_RSA.value,
        "ciphertext": ciphertext,
        "iv": iv,
        "encrypted_keys": encrypted_keys,
        "signal_message_type": None,
    }