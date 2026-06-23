"""CLI Signal Protocol proof — Engine 8 Step 8.8 full sign-off."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.signal_proof import (  # noqa: E402
    run_signal_proof,
    run_signal_proof_step_81,
    run_signal_proof_step_82,
    run_signal_proof_step_83,
    run_signal_proof_step_84,
    run_signal_proof_step_85,
    run_signal_proof_step_86,
    run_signal_proof_step_87,
    run_signal_proof_step_88,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="SSC Signal Protocol proof")
    parser.add_argument("--step-81-only", action="store_true")
    parser.add_argument("--step-88-only", action="store_true", help="Alias for full 8.8 proof")
    args = parser.parse_args()

    if args.step_81_only:
        report = run_signal_proof_step_81()
        label = "8.1"
    elif args.step_88_only:
        report = run_signal_proof_step_88()
        label = "8.8"
    else:
        report = run_signal_proof()
        label = "8.8"

    print(json.dumps(report.to_dict(), indent=2))
    if report.passed:
        print(f"\nSIGNAL PROOF ({label}) PASSED")
        return 0
    failed = [c.name for c in report.checks if not c.passed]
    print(f"\nSIGNAL PROOF ({label}) FAILED: {failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())