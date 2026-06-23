"""
Engine 8 test gate — Step 8.8 sign-off runner.

Runs Engine 8 unit tests, live-server integration checks, and signal proof.
Usage:
  venv\\Scripts\\python.exe scripts/run_engine8_gate.py
  venv\\Scripts\\python.exe scripts/run_engine8_gate.py --step-87-only
  venv\\Scripts\\python.exe scripts/run_engine8_gate.py --skip-integration
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from core.signal_proof import (  # noqa: E402
    ENGINE8_INTEGRATION_MODULES,
    ENGINE8_UNIT_MODULES,
    run_signal_proof,
    run_signal_proof_step_81,
    run_signal_proof_step_82,
    run_signal_proof_step_83,
    run_signal_proof_step_84,
    run_signal_proof_step_85,
    run_signal_proof_step_86,
    run_signal_proof_step_87,
)

PYTHON = ROOT / "venv" / "Scripts" / "python.exe"
if not PYTHON.is_file():
    PYTHON = Path(sys.executable)

BASE = __import__("os").environ.get("REACT_APP_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
API = f"{BASE}/api"


def _run_pytest(paths: list[str], label: str) -> int:
    print(f"\n== {label} ==")
    cmd = [str(PYTHON), "-m", "pytest", *paths, "-q", "--tb=short"]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode == 0:
        print(f"  OK  {label}")
    else:
        print(f"  FAIL {label} (exit {result.returncode})")
    return result.returncode


def _server_up() -> bool:
    try:
        r = requests.get(f"{API}/", timeout=5)
        return r.status_code == 200 and r.json().get("status") == "ok"
    except Exception:
        return False


def _run_signal_proof_cli() -> int:
    print("\n== Signal proof (step 8.8) ==")
    cmd = [str(PYTHON), "scripts/signal_proof.py"]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode == 0:
        print("  OK  signal proof")
    else:
        print(f"  FAIL signal proof (exit {result.returncode})")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="SSC Engine 8 test gate")
    parser.add_argument("--step-81-only", action="store_true", help="Run 8.1 policy proof only")
    parser.add_argument("--step-82-only", action="store_true", help="Run through 8.2 proof")
    parser.add_argument("--step-83-only", action="store_true", help="Run through 8.3 proof")
    parser.add_argument("--step-84-only", action="store_true", help="Run through 8.4 proof")
    parser.add_argument("--step-85-only", action="store_true", help="Run through 8.5 proof")
    parser.add_argument("--step-86-only", action="store_true", help="Run through 8.6 proof")
    parser.add_argument("--step-87-only", action="store_true", help="Run through 8.7 proof")
    parser.add_argument("--skip-integration", action="store_true")
    parser.add_argument("--skip-proof", action="store_true")
    args = parser.parse_args()

    step_only = any(
        getattr(args, f"step_{s.replace('.', '_')}_only")
        for s in ("81", "82", "83", "84", "85", "86", "87")
    )

    print(f"Engine 8 gate -> {ROOT}")
    exit_code = 0

    if args.step_81_only:
        report = run_signal_proof_step_81()
    elif args.step_82_only:
        report = run_signal_proof_step_82()
    elif args.step_83_only:
        report = run_signal_proof_step_83()
    elif args.step_84_only:
        report = run_signal_proof_step_84()
    elif args.step_85_only:
        report = run_signal_proof_step_85()
    elif args.step_86_only:
        report = run_signal_proof_step_86()
    elif args.step_87_only:
        report = run_signal_proof_step_87()
    else:
        report = run_signal_proof()

    print(report.to_dict())
    if not report.passed:
        print("FAIL: signal proof")
        return 1
    print("OK: signal proof")

    exit_code |= _run_pytest(list(ENGINE8_UNIT_MODULES), "Engine 8 unit tests")

    if step_only:
        step_labels = {
            "step_81_only": "8.1",
            "step_82_only": "8.2",
            "step_83_only": "8.3",
            "step_84_only": "8.4",
            "step_85_only": "8.5",
            "step_86_only": "8.6",
            "step_87_only": "8.7",
        }
        for attr, label in step_labels.items():
            if getattr(args, attr):
                print(f"\nENGINE 8 STEP {label} GATE PASSED")
                return exit_code
        return exit_code

    if not args.skip_integration:
        if not _server_up():
            print("\n== Engine 8 integration ==")
            print(f"  FAIL backend not reachable at {API}/")
            exit_code |= 1
        else:
            exit_code |= _run_pytest(list(ENGINE8_INTEGRATION_MODULES), "Engine 8 integration")

    if not args.skip_proof:
        exit_code |= _run_signal_proof_cli()

    print("\n---")
    if exit_code == 0:
        print("ENGINE 8 GATE PASSED")
    else:
        print("ENGINE 8 GATE FAILED")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())