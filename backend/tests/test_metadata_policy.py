"""Engine 4 Step 4.1 — metadata policy manifest."""
from core.client_footprint_policy import ENGINE3_STEPS
from core.metadata_policy import (
    CONTACTS_ALLOWED_FIELDS,
    CONTACTS_PERSISTENT,
    ENGINE4_STEPS,
    GENERIC_PUSH_BODY,
    GENERIC_PUSH_TITLE,
    METADATA_GAPS,
    METADATA_SURFACES,
    accepted_tradeoffs,
    engine4_complete,
)


def test_engine3_prerequisite_complete():
    assert all(done for _, _, done in ENGINE3_STEPS)


def test_engine4_all_steps_marked_complete():
    for step_id in ("4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7"):
        step = next(s for s in ENGINE4_STEPS if s[0] == step_id)
        assert step[2] is True, f"step {step_id} must be complete"


def test_engine4_complete_helper():
    assert engine4_complete() is True


def test_generic_push_constants():
    assert GENERIC_PUSH_TITLE == "SSC"
    assert GENERIC_PUSH_BODY == "New activity"


def test_metadata_surfaces_include_last_seen_and_push():
    assert "last_seen" in METADATA_SURFACES
    assert "push_visible" in METADATA_SURFACES
    assert "contacts_graph" in METADATA_SURFACES


def test_contacts_tradeoff_documented():
    assert CONTACTS_PERSISTENT is True
    assert "user_id" in CONTACTS_ALLOWED_FIELDS
    assert "contact_id" in CONTACTS_ALLOWED_FIELDS
    tradeoffs = accepted_tradeoffs()
    assert any(s.surface_id == "contacts_graph" for s in tradeoffs)


def test_engine4_gaps_m1_m3_resolved():
    resolved = {g.gap_id for g in METADATA_GAPS if g.resolved}
    assert "M1" in resolved
    assert "M2" in resolved
    assert "M3" in resolved