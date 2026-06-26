"""Security observability helpers for structured anomaly events."""
from __future__ import annotations

from typing import Any

from core.logging_config import logger


def _normalize(value: Any) -> str:
    text = str(value)
    return text.replace(" ", "_")


def security_event(event: str, *, severity: str = "warning", **fields: Any) -> None:
    extras = " ".join(f"{k}={_normalize(v)}" for k, v in sorted(fields.items()))
    message = f"security-event event={_normalize(event)}"
    if extras:
        message = f"{message} {extras}"

    if severity == "error":
        logger.error(message)
    elif severity == "info":
        logger.info(message)
    else:
        logger.warning(message)
