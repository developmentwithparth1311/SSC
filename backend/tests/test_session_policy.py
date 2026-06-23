"""Engine 5 Step 5.1 — session hardening policy manifest."""
from pathlib import Path

from core.metadata_policy import engine4_complete
from core.session_policy import (
    ENGINE5_STEPS,
    LEGACY_JWT_LOCAL_STORAGE_KEY,
    SESSION_COOKIE_NAME,
    TESTING_STRATEGY,
    engine5_complete,
    engine5_prerequisite_met,
)

BACKEND = Path(__file__).resolve().parents[1]


def test_engine4_prerequisite_for_engine5():
    assert engine4_complete()
    assert engine5_prerequisite_met()


def test_engine5_steps_5_1_through_5_7_complete():
    done = {step_id: complete for step_id, _, complete in ENGINE5_STEPS}
    for step_id in ("5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7"):
        assert done[step_id] is True, f"step {step_id} must be complete"


def test_engine5_gap_s1_resolved():
    from core.session_policy import SESSION_GAPS
    s1 = next(g for g in SESSION_GAPS if g.gap_id == "S1")
    assert s1.resolved is True


def test_engine5_gap_s2_resolved():
    from core.session_policy import SESSION_GAPS
    s2 = next(g for g in SESSION_GAPS if g.gap_id == "S2")
    assert s2.resolved is True


def test_engine5_fully_complete():
    assert engine5_complete() is True


def test_session_cookie_constants():
    assert SESSION_COOKIE_NAME == "session_token"
    assert LEGACY_JWT_LOCAL_STORAGE_KEY == "ssc_token"


def test_testing_strategy_locked():
    assert "Firebase App Tester" in TESTING_STRATEGY["real_testers"]
    assert "founder" in TESTING_STRATEGY["lan_localhost"].lower()
    assert "2026-06-28" in TESTING_STRATEGY["domain_https"]


def test_session_charter_exists():
    charter = BACKEND.parent / "memory" / "SESSION_HARDENING_CHARTER.md"
    text = charter.read_text(encoding="utf-8")
    assert "**5.1**" in text
    assert "Firebase App Tester" in text
    assert "localStorage" in text