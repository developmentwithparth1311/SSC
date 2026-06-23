"""Engine 4 Steps 4.2–4.3 — last_seen minimization."""
from datetime import datetime, timedelta, timezone

from core.last_seen import (
    coarsen_last_seen,
    last_seen_expired,
    project_peer_presence,
    project_user_for_peer,
    should_write_last_seen,
)
from core.metadata_policy import LAST_SEEN_STORAGE_TTL_DAYS, LAST_SEEN_WRITE_INTERVAL_SEC
from core.utils import iso


def _iso_ago(seconds: float) -> str:
    return iso(datetime.now(timezone.utc) - timedelta(seconds=seconds))


def test_should_write_last_seen_throttles_recent():
    raw = _iso_ago(60)
    assert should_write_last_seen(raw) is False


def test_should_write_last_seen_allows_after_interval():
    raw = _iso_ago(LAST_SEEN_WRITE_INTERVAL_SEC + 10)
    assert should_write_last_seen(raw) is True


def test_last_seen_expired_after_ttl():
    raw = _iso_ago(LAST_SEEN_STORAGE_TTL_DAYS * 86400 + 3600)
    assert last_seen_expired(raw) is True


def test_project_peer_presence_online_hides_timestamp():
    raw = _iso_ago(60)
    out = project_peer_presence(raw)
    assert out["online"] is True
    assert out["last_seen"] is None


def test_project_peer_presence_coarsens_offline():
    raw = _iso_ago(2 * 3600)
    out = project_peer_presence(raw)
    assert out["online"] is False
    assert out["last_seen"] is not None
    assert out["last_seen"] != raw


def test_coarsen_buckets_15m_for_recent():
    dt = datetime(2026, 6, 23, 14, 37, 22, tzinfo=timezone.utc)
    now = datetime(2026, 6, 23, 15, 0, 0, tzinfo=timezone.utc)
    coarsened = coarsen_last_seen(iso(dt), now=now)
    assert coarsened.endswith("+00:00") or "+00:00" in coarsened
    parsed = datetime.fromisoformat(coarsened)
    assert parsed.minute % 15 == 0
    assert parsed.second == 0


def test_project_user_for_peer_adds_online_flag():
    user = {
        "user_id": "u_a",
        "username": "alice",
        "last_seen": _iso_ago(120),
    }
    out = project_user_for_peer(user)
    assert out["online"] is True
    assert out["last_seen"] is None
    assert out["username"] == "alice"