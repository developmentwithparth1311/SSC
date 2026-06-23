"""CLI session hardening proof — Engine 5 Step 5.7."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.session_proof import run_session_proof  # noqa: E402


def main() -> int:
    report = run_session_proof()
    print(json.dumps(report.to_dict(), indent=2))
    if report.passed:
        print("\nSESSION PROOF PASSED")
        return 0
    failed = [c.name for c in report.checks if not c.passed]
    print(f"\nSESSION PROOF FAILED: {failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())