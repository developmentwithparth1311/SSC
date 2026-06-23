"""Engine 9 gate manifest."""
from pathlib import Path

from core.translation_policy import ENGINE9_STEPS, engine9_complete, run_translation_proof

BACKEND = Path(__file__).resolve().parents[1]


def test_engine9_all_steps_marked_complete():
    for step_id in ("9.1", "9.2", "9.3", "9.4"):
        step = next(s for s in ENGINE9_STEPS if s[0] == step_id)
        assert step[2] is True, f"Engine 9 step {step_id} must be complete"


def test_engine9_complete_helper():
    assert engine9_complete() is True


def test_engine9_gate_script_exists():
    assert (BACKEND / "scripts" / "run_engine9_gate.py").is_file()


def test_translation_proof_passes():
    report = run_translation_proof()
    failed = [c.name for c in report.checks if not c.passed]
    assert report.passed, f"proof failures: {failed}"