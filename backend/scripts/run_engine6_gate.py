#!/usr/bin/env python3
"""Engine 6 gate — push / own-metal evaluation policy."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("== Engine 6 unit tests ==")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_engine6_policy.py", "-q"],
        cwd=ROOT,
    )
    if r.returncode != 0:
        print("\nENGINE 6 GATE FAILED")
        return 1
    print("\nENGINE 6 GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())