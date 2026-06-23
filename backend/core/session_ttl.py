"""Canonical session TTL — single source aligned with session_policy (Engine 5.6)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from core.session_policy import SESSION_JWT_TTL_DAYS


def session_ttl_timedelta() -> timedelta:
    return timedelta(days=SESSION_JWT_TTL_DAYS)


def session_ttl_seconds() -> int:
    return SESSION_JWT_TTL_DAYS * 24 * 3600


def session_expires_at(now: datetime | None = None) -> datetime:
    base = now or datetime.now(timezone.utc)
    return base + session_ttl_timedelta()


def jwt_exp_timestamp(now: datetime | None = None) -> int:
    return int(session_expires_at(now).timestamp())