"""Engine 5 Step 5.6 — production Redis revocation gate + session TTL alignment."""
from unittest.mock import MagicMock, patch

import jwt
import pytest

from core.auth import jwt_ttl_seconds, make_jwt, store_user_session
from core.config import JWT_SECRET
from core.health_checks import check_redis, full_health
from core.session_cookie import session_cookie_max_age
from core.session_policy import ENGINE5_STEPS, SESSION_GAPS, SESSION_JWT_TTL_DAYS
from core.session_production import validate_production_redis
from core.session_ttl import session_expires_at, session_ttl_seconds
from core.token_revocation import revoke_token
from security import validate_environment


def test_engine5_step_5_6_marked_complete():
    done = {step_id: complete for step_id, _, complete in ENGINE5_STEPS}
    assert done["5.6"] is True


def test_s2_gap_resolved():
    s2 = next(g for g in SESSION_GAPS if g.gap_id == "S2")
    assert s2.resolved is True


def test_session_ttl_single_source():
    assert session_ttl_seconds() == SESSION_JWT_TTL_DAYS * 86400
    assert session_cookie_max_age() == session_ttl_seconds()


def test_make_jwt_exp_matches_policy():
    token = make_jwt("user_test")
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    ttl = int(payload["exp"]) - int(payload["iat"])
    assert ttl == session_ttl_seconds()


def test_jwt_ttl_seconds_fallback_matches_policy():
    assert jwt_ttl_seconds("not-a-jwt") == session_ttl_seconds()


@pytest.mark.asyncio
async def test_store_user_session_expires_at_aligned():
    captured = {}

    async def fake_update_one(_filter, update, upsert=False):
        captured["expires_at"] = update["$set"]["expires_at"]

    with patch("core.auth.db") as mock_db:
        mock_db.user_sessions.update_one = fake_update_one
        token = make_jwt("user_ttl")
        await store_user_session("user_ttl", token)
    delta = (captured["expires_at"] - session_expires_at()).total_seconds()
    assert abs(delta) < 2


def test_validate_production_redis_requires_url():
    with patch("core.session_production.is_production_env", return_value=True):
        with pytest.raises(RuntimeError, match="REDIS_URL"):
            validate_production_redis(None, "")


def test_validate_production_redis_requires_client():
    with patch("core.session_production.is_production_env", return_value=True):
        with pytest.raises(RuntimeError, match="unavailable"):
            validate_production_redis(None, "redis://localhost:6379/0")


def test_validate_production_redis_requires_ping():
    bad = MagicMock()
    bad.ping.side_effect = ConnectionError("down")
    with patch("core.session_production.is_production_env", return_value=True):
        with pytest.raises(RuntimeError, match="unreachable"):
            validate_production_redis(bad, "redis://localhost:6379/0")


def test_validate_production_redis_skipped_in_dev():
    validate_production_redis(None, "")


def test_validate_environment_fails_production_without_redis(monkeypatch):
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("DB_NAME", "ssc_test")
    monkeypatch.setenv("JWT_SECRET", "x" * 48)
    with patch("core.session_production.is_production_env", return_value=True):
        with patch("security._redis", None):
            with patch("security._redis_url", ""):
                with pytest.raises(RuntimeError, match="REDIS_URL"):
                    validate_environment()


def test_revoke_token_noop_in_dev_without_redis():
    with patch("core.token_revocation._redis", None):
        with patch("core.session_production.is_production_env", return_value=False):
            revoke_token("tok", 3600)


def test_revoke_token_raises_in_production_without_redis():
    with patch("core.token_revocation._redis", None):
        with patch("core.session_production.is_production_env", return_value=True):
            with pytest.raises(RuntimeError, match="revocation requires Redis"):
                revoke_token("tok", 3600)


@pytest.mark.asyncio
async def test_check_redis_error_in_production_when_disabled():
    with patch("core.health_checks.get_rate_limit_backend", return_value="memory"):
        with patch("core.health_checks.ENV", "production"):
            result = await check_redis()
    assert result["status"] == "error"


@pytest.mark.asyncio
async def test_full_health_error_in_production_without_redis():
    with patch("core.health_checks.check_mongo", return_value={"status": "ok"}):
        with patch(
            "core.health_checks.check_redis",
            return_value={"status": "error", "detail": "missing"},
        ):
            with patch("core.health_checks.ENV", "production"):
                result = await full_health()
    assert result["status"] == "error"