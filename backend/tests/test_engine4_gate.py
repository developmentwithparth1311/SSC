"""Engine 4 Step 4.7 — test gate manifest and sign-off checks."""
from pathlib import Path

from core.metadata_proof import (
    ENGINE4_INTEGRATION_MODULES,
    ENGINE4_SCRIPTS,
    ENGINE4_UNIT_MODULES,
    run_metadata_proof,
)
from core.metadata_policy import ENGINE4_STEPS, engine4_complete
from core.client_footprint_policy import ENGINE3_STEPS

BACKEND = Path(__file__).resolve().parents[1]


def test_engine3_prerequisite_for_engine4_gate():
    assert all(done for _, _, done in ENGINE3_STEPS), "Engine 3 must be complete before Engine 4 gate"


def test_engine4_all_steps_marked_complete():
    for step_id in ("4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7"):
        step = next(s for s in ENGINE4_STEPS if s[0] == step_id)
        assert step[2] is True, f"Engine 4 step {step_id} must be complete for gate sign-off"


def test_engine4_complete_helper():
    assert engine4_complete() is True


def test_engine4_unit_modules_exist():
    missing = [m for m in ENGINE4_UNIT_MODULES if not (BACKEND / m).is_file()]
    assert missing == [], f"missing unit test modules: {missing}"


def test_engine4_integration_module_exists():
    for m in ENGINE4_INTEGRATION_MODULES:
        assert (BACKEND / m).is_file(), m


def test_engine4_gate_scripts_exist():
    missing = [s for s in ENGINE4_SCRIPTS if not (BACKEND / s).is_file()]
    assert missing == [], f"missing gate scripts: {missing}"


def test_run_engine4_gate_references_unit_and_integration():
    text = (BACKEND / "scripts" / "run_engine4_gate.py").read_text(encoding="utf-8")
    assert "ENGINE4_INTEGRATION_MODULES" in text
    assert "ENGINE4_UNIT_MODULES" in text
    assert "metadata_proof" in text


def test_metadata_proof_passes():
    report = run_metadata_proof()
    failed = [c.name for c in report.checks if not c.passed]
    assert report.passed, f"proof failures: {failed}"


def test_charter_documents_engine4_gate():
    charter = BACKEND.parent / "memory" / "METADATA_MINIMIZATION_CHARTER.md"
    text = charter.read_text(encoding="utf-8")
    assert "**4.7**" in text
    assert "run_engine4_gate.py" in text
    assert "metadata_proof.py" in text