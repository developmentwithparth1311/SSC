"""Signal status/stories policy — Engine 8.12 (signal_status_v1 Sender Keys)."""
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from core.signal_message_policy import (
    SignalMessageValidationError,
    validate_signal_ciphertext,
)
from core.signal_policy import ProtocolVersion

ALLOWED_STATUS_SIGNAL_MESSAGE_TYPES = frozenset({7})


def validate_distribution_id(value: Optional[str]) -> str:
    if not value or not isinstance(value, str):
        raise SignalMessageValidationError("distribution_id required for signal_status_v1")
    raw = value.strip()
    try:
        uuid.UUID(raw)
    except ValueError as exc:
        raise SignalMessageValidationError("distribution_id must be a UUID") from exc
    return raw


def validate_status_payload(
    *,
    protocol: str,
    ciphertext: str,
    iv: Optional[str],
    encrypted_keys: Optional[Dict[str, Any]],
    signal_message_type: Optional[int],
    distribution_id: Optional[str],
    author_id: str,
) -> Dict[str, Any]:
    """Return normalized storage fields for a new status."""
    raw = (protocol or ProtocolVersion.LEGACY_RSA.value).strip().lower()
    if raw == ProtocolVersion.SIGNAL_STATUS_V1.value:
        if iv:
            raise SignalMessageValidationError("iv not allowed for signal_status_v1")
        if encrypted_keys:
            raise SignalMessageValidationError("encrypted_keys not allowed for signal_status_v1")
        if not isinstance(signal_message_type, int) or signal_message_type not in ALLOWED_STATUS_SIGNAL_MESSAGE_TYPES:
            raise SignalMessageValidationError("signal_message_type must be 7 (senderkey) for signal_status_v1")
        return {
            "protocol": ProtocolVersion.SIGNAL_STATUS_V1.value,
            "ciphertext": validate_signal_ciphertext(ciphertext),
            "signal_message_type": signal_message_type,
            "distribution_id": validate_distribution_id(distribution_id),
            "iv": None,
            "encrypted_keys": None,
            "author_id": author_id,
        }

    if raw != ProtocolVersion.LEGACY_RSA.value:
        raise SignalMessageValidationError(f"unsupported status protocol: {raw}")
    if not iv:
        raise SignalMessageValidationError("iv required for legacy_rsa status")
    if not encrypted_keys:
        raise SignalMessageValidationError("encrypted_keys required for legacy_rsa status")
    if author_id not in encrypted_keys:
        raise SignalMessageValidationError("encrypted_keys must include author")
    return {
        "protocol": ProtocolVersion.LEGACY_RSA.value,
        "ciphertext": ciphertext,
        "iv": iv,
        "encrypted_keys": encrypted_keys,
        "signal_message_type": None,
        "distribution_id": None,
    }