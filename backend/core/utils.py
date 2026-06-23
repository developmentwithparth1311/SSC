"""Shared utility helpers."""
from datetime import datetime, timezone
from typing import Optional

from core.config import BANNED_SUBSTRINGS, USERNAME_RE


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def validate_username(username: str) -> Optional[str]:
    if not username:
        return "Username is required"
    if len(username) < 4 or len(username) > 12:
        return "Username must be 4–12 characters"
    if not USERNAME_RE.match(username):
        return "Only letters, digits and underscore. Must start with a letter. No emoji or symbols."
    low = username.lower().replace("_", "")
    for sub in BANNED_SUBSTRINGS:
        if sub in low:
            return "Username contains a forbidden term"
    return None