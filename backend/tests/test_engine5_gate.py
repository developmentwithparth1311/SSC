"""Engine 5 Step 5.7 — test gate manifest and sign-off checks."""
from pathlib import Path

from core.metadata_policy import ENGINE4_STEPS
from core.session_policy import ENGINE5_STEPS, engine5_complete
from core.session_proof import (
    ENGINE5_INTEGRATION_MODULES,
    ENGINE5_SCRIPTS,
    ENGINE5_UNIT_MODULES,
    run_session_proof,
)

BACKEND = Path(__file__).resolve().parents[1]


def test_engine4_prerequisite_for_engine5_gate():
    assert all(done for _, _, done in ENGINE4_STEPS), "Engine 4 must be complete before Engine 5 gate"


def test_engine5_all_steps_marked_complete():
    for step_id in ("5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7"):
        step = next(s for s in ENGINE5_STEPS if s[0] == step_id)
        assert step[2] is True, f"Engine 5 step {step_id} must be complete for gate sign-off"


def test_engine5_complete_helper():
    assert engine5_complete() is True


def test_engine5_unit_modules_exist():
    missing = [m for m in ENGINE5_UNIT_MODULES if not (BACKEND / m).is_file()]
    assert missing == [], f"missing unit test modules: {missing}"


def test_engine5_integration_module_exists():
    for m in ENGINE5_INTEGRATION_MODULES:
        assert (BACKEND / m).is_file(), m


def test_engine5_gate_scripts_exist():
    missing = [s for s in ENGINE5_SCRIPTS if not (BACKEND / s).is_file()]
    assert missing == [], f"missing gate scripts: {missing}"


def test_run_engine5_gate_references_unit_and_integration():
    text = (BACKEND / "scripts" / "run_engine5_gate.py").read_text(encoding="utf-8")
    assert "ENGINE5_INTEGRATION_MODULES" in text
    assert "ENGINE5_UNIT_MODULES" in text
    assert "session_proof" in text


def test_session_proof_passes():
    report = run_session_proof()
    failed = [c.name for c in report.checks if not c.passed]
    assert report.passed, f"proof failures: {failed}"


def test_charter_documents_engine5_gate():
    charter = BACKEND.parent / "memory" / "SESSION_HARDENING_CHARTER.md"
    text = charter.read_text(encoding="utf-8")
    assert "**5.7**" in text
    assert "run_engine5_gate.py" in text
    assert "session_proof.py" in text