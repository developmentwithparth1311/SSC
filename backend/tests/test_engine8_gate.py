"""Engine 8 Step 8.8 — test gate manifest and sign-off checks."""
from pathlib import Path

from core.signal_policy import ENGINE8_STEPS, engine8_complete
from core.signal_proof import (
    ENGINE8_INTEGRATION_MODULES,
    ENGINE8_SCRIPTS,
    ENGINE8_UNIT_MODULES,
    run_signal_proof,
)

BACKEND = Path(__file__).resolve().parents[1]


def test_engine5_prerequisite_steps_done():
    from core.signal_policy import engine8_prerequisites_met

    assert engine8_prerequisites_met() is True


def test_engine8_all_steps_marked_complete():
    for step_id in ("8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8"):
        step = next(s for s in ENGINE8_STEPS if s[0] == step_id)
        assert step[2] is True, f"Engine 8 step {step_id} must be complete for gate sign-off"


def test_engine8_complete_helper():
    assert engine8_complete() is True


def test_engine8_unit_modules_exist():
    missing = [m for m in ENGINE8_UNIT_MODULES if not (BACKEND / m).is_file()]
    assert missing == [], f"missing unit test modules: {missing}"


def test_engine8_integration_module_exists():
    for m in ENGINE8_INTEGRATION_MODULES:
        assert (BACKEND / m).is_file(), m


def test_engine8_gate_scripts_exist():
    missing = [s for s in ENGINE8_SCRIPTS if not (BACKEND / s).is_file()]
    assert missing == [], f"missing gate scripts: {missing}"


def test_run_engine8_gate_references_unit_and_integration():
    text = (BACKEND / "scripts" / "run_engine8_gate.py").read_text(encoding="utf-8")
    assert "ENGINE8_INTEGRATION_MODULES" in text
    assert "ENGINE8_UNIT_MODULES" in text
    assert "run_signal_proof" in text
    assert "signal_proof.py" in text


def test_signal_proof_passes():
    report = run_signal_proof()
    failed = [c.name for c in report.checks if not c.passed]
    assert report.passed, f"proof failures: {failed}"


def test_charter_documents_engine8_gate():
    charter = BACKEND.parent / "memory" / "SIGNAL_PROTOCOL_CHARTER.md"
    text = charter.read_text(encoding="utf-8")
    assert "**8.8**" in text
    assert "run_engine8_gate.py" in text
    assert "signal_proof.py" in text