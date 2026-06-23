"""CLI metadata minimization proof — Engine 4 Step 4.7."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.metadata_proof import run_metadata_proof  # noqa: E402


def main() -> int:
    report = run_metadata_proof()
    print(json.dumps(report.to_dict(), indent=2))
    if report.passed:
        print("\nMETADATA PROOF PASSED")
        return 0
    failed = [c.name for c in report.checks if not c.passed]
    print(f"\nMETADATA PROOF FAILED: {failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())