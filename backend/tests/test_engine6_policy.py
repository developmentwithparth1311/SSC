"""Engine 6 — push / own-metal evaluation policy tests."""
from pathlib import Path

from core.engine6_policy import (
    ENGINE6_STEPS,
    OWN_METAL_DECISIONS,
    PUSH_PATH_DECISIONS,
    engine6_complete,
    engine6_evaluation_complete,
)


def test_engine6_charter_exists():
    charter = Path(__file__).resolve().parents[2] / "memory" / "ENGINE_6_CHARTER.md"
    text = charter.read_text(encoding="utf-8")
    assert "FCM" in text
    assert "deferred post-investors" in text.lower() or "Deferred post-investors" in text


def test_engine6_evaluation_steps_done():
    done = {step_id: flag for step_id, _, flag in ENGINE6_STEPS}
    assert done["6.1"] is True
    assert done["6.2"] is True
    assert done["6.3"] is False


def test_engine6_evaluation_complete_helper():
    assert engine6_evaluation_complete() is True
    assert engine6_complete() is False


def test_push_paths_keep_fcm_and_vapid():
    assert PUSH_PATH_DECISIONS["fcm_android"] == "keep"
    assert PUSH_PATH_DECISIONS["web_vapid"] == "keep"
    assert PUSH_PATH_DECISIONS["unified_push_self_host"] == "deferred"


def test_own_metal_mongo_deferred():
    assert OWN_METAL_DECISIONS["mongodb"] == "deferred_post_investors"
    assert OWN_METAL_DECISIONS["api_compute"] == "keep_cloud_run"