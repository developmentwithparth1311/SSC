"""JWT revocation via Redis (logout / panic)."""
import hashlib
from typing import Optional

from security import _redis


def _token_key(token: str) -> str:
    digest = hashlib.sha256(token.encode()).hexdigest()
    return f"ssc:revoked:{digest}"


def revoke_token(token: str, ttl_seconds: int) -> None:
    if not _redis or not token or ttl_seconds < 1:
        return
    try:
        _redis.setex(_token_key(token), ttl_seconds, "1")
    except Exception:
        pass


def is_token_revoked(token: str) -> bool:
    if not _redis or not token:
        return False
    try:
        return bool(_redis.exists(_token_key(token)))
    except Exception:
        return False