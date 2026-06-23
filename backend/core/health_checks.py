"""Dependency health probes for monitoring and load balancers."""
from typing import Any, Dict

from core.config import ENV
from core.database import db
from security import get_rate_limit_backend, ping_redis


async def check_mongo() -> Dict[str, Any]:
    try:
        await db.command("ping")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": type(e).__name__}


async def check_redis() -> Dict[str, Any]:
    backend = get_rate_limit_backend()
    if backend == "memory":
        return {"status": "disabled", "detail": "REDIS_URL not set — per-worker in-memory limits"}
    result = ping_redis()
    if result:
        return {"status": "ok"}
    return {"status": "error", "detail": "Redis unreachable"}


async def full_health() -> Dict[str, Any]:
    mongo = await check_mongo()
    redis = await check_redis()
    parts = [mongo["status"], redis["status"]]
    if "error" in parts:
        overall = "error"
    elif "disabled" in parts or ENV != "production":
        overall = "ok"
    else:
        overall = "ok" if all(p == "ok" for p in parts) else "degraded"
    return {
        "status": overall,
        "env": ENV,
        "mongo": mongo,
        "redis": redis,
        "rate_limit_backend": get_rate_limit_backend(),
        "version": "0.4-standalone",
    }