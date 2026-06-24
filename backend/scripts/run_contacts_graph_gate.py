#!/usr/bin/env python3
"""Contacts graph privacy gate."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("== Contacts graph privacy tests ==")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_contact_graph_privacy.py", "-q"],
        cwd=ROOT,
    )
    if proc.returncode != 0:
        print("\nCONTACTS GRAPH GATE FAILED")
        return proc.returncode
    print("\nCONTACTS GRAPH GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())