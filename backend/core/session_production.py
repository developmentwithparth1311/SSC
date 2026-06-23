"""Production session requirements — Engine 5 Step 5.6."""
from __future__ import annotations

from typing import Any, Optional

from core.config import ENV, REDIS_URL


def is_production_env() -> bool:
    return ENV == "production"


def validate_production_redis(
    redis_client: Any,
    redis_url: Optional[str] = None,
) -> None:
    """Fail fast at startup when production cannot revoke sessions."""
    if not is_production_env():
        return

    url = (redis_url if redis_url is not None else REDIS_URL).strip()
    if not url:
        raise RuntimeError(
            "ENV=production requires REDIS_URL for JWT revocation and distributed rate limits"
        )
    if redis_client is None:
        raise RuntimeError(
            "ENV=production but Redis is unavailable — session revocation cannot work"
        )
    try:
        if not redis_client.ping():
            raise RuntimeError("ENV=production but Redis ping returned false")
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(
            f"ENV=production but Redis is unreachable ({type(exc).__name__})"
        ) from exc


def assert_revocation_redis_available(redis_client: Any) -> None:
    """Called on logout/panic — production must not silently skip revocation."""
    if not is_production_env():
        return
    if redis_client is None:
        raise RuntimeError(
            "Session revocation requires Redis in production"
        )