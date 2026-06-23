"""
Engine 9 test gate — on-device translation sign-off.

Usage:
  venv\\Scripts\\python.exe scripts/run_engine9_gate.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.translation_policy import run_translation_proof

PYTHON = ROOT / "venv" / "Scripts" / "python.exe"
if not PYTHON.is_file():
    PYTHON = Path(sys.executable)

UNIT_TESTS = [
    "tests/test_translation_guard.py",
    "tests/test_engine9_gate.py",
    "tests/test_translation_policy_engine9.py",
]


def main() -> int:
    print("\n== Engine 9 unit tests ==")
    cmd = [str(PYTHON), "-m", "pytest", *UNIT_TESTS, "-q", "--tb=short"]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode

    print("\n== Engine 9 translation proof ==")
    report = run_translation_proof()
    for check in report.checks:
        status = "OK" if check.passed else "FAIL"
        print(f"  {status}  {check.name}: {check.detail}")
    if not report.passed:
        return 1
    print("\nEngine 9 gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())