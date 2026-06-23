"""Pytest session setup: load backend .env and clear Redis rate-limit buckets."""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@pytest.fixture(scope="session", autouse=True)
def _clear_redis_rate_limits():
    """Fresh rate-limit counters so integration tests do not inherit prior runs."""
    url = os.environ.get("REDIS_URL", "").strip()
    if not url:
        return
    try:
        import redis

        redis.from_url(url).flushdb()
    except Exception:
        pass


def mongo_client():
    """Motor client matching production TLS settings."""
    import certifi
    from motor.motor_asyncio import AsyncIOMotorClient

    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    if mongo_url.startswith("mongodb+srv://") or "tls=true" in mongo_url:
        return AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where())
    return AsyncIOMotorClient(mongo_url)