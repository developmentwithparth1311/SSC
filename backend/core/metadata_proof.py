"""Metadata minimization proof — Engine 4 Step 4.7. See memory/METADATA_MINIMIZATION_CHARTER.md."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

from core.client_footprint_policy import engine3_complete
from core.metadata_policy import ENGINE4_STEPS, METADATA_GAPS, engine4_complete

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]

ENGINE4_UNIT_MODULES: Tuple[str, ...] = (
    "tests/test_metadata_policy.py",
    "tests/test_last_seen.py",
    "tests/test_push_payload.py",
    "tests/test_engine4_gate.py",
)

ENGINE4_INTEGRATION_MODULES: Tuple[str, ...] = (
    "tests/test_engine4_integration.py",
)

ENGINE4_SCRIPTS: Tuple[str, ...] = (
    "scripts/run_engine4_gate.py",
    "scripts/metadata_proof.py",
)

ENFORCEMENT_PATHS: Tuple[str, ...] = (
    "memory/METADATA_MINIMIZATION_CHARTER.md",
    "backend/core/metadata_policy.py",
    "backend/core/last_seen.py",
    "backend/core/push_payload.py",
    "backend/push.py",
    "backend/native_push.py",
    "backend/core/conversation_meta.py",
    "frontend/public/sw.js",
    "frontend/src/lib/presence.js",
)

DEFERRED_ENGINE4_GAPS = frozenset({"M4", "M5", "M6"})


@dataclass
class ProofCheck:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class MetadataProofReport:
    checks: List[ProofCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [{"name": c.name, "passed": c.passed, "detail": c.detail} for c in self.checks],
        }


def _check_engine3_prerequisite() -> ProofCheck:
    ok = engine3_complete()
    return ProofCheck(
        name="engine3_prerequisite",
        passed=ok,
        detail="Engine 3 steps 3.1–3.7 complete" if ok else "Engine 3 must be complete before Engine 4 sign-off",
    )


def _check_engine4_steps() -> ProofCheck:
    incomplete = [step_id for step_id, _, done in ENGINE4_STEPS if not done]
    ok = not incomplete
    return ProofCheck(
        name="engine4_steps_complete",
        passed=ok,
        detail="all steps done" if ok else f"incomplete: {', '.join(incomplete)}",
    )


def _check_engine4_complete_helper() -> ProofCheck:
    ok = engine4_complete()
    return ProofCheck(
        name="engine4_complete_helper",
        passed=ok,
        detail="engine4_complete() is True" if ok else "engine4_complete() returned False",
    )


def _check_engine4_gaps() -> ProofCheck:
    open_ids = {g.gap_id for g in METADATA_GAPS if not g.resolved}
    unexpected = open_ids - DEFERRED_ENGINE4_GAPS
    ok = not unexpected
    return ProofCheck(
        name="engine4_gaps_resolved",
        passed=ok,
        detail="M1–M3 resolved; M4–M6 deferred" if ok else f"open gaps: {sorted(unexpected)}",
    )


def _check_push_generic_enforcement() -> ProofCheck:
    push_py = BACKEND_ROOT / "push.py"
    if not push_py.is_file():
        return ProofCheck(name="push_generic", passed=False, detail="push.py missing")
    text = push_py.read_text(encoding="utf-8")
    forbidden = ["Sent a photo", "Sent a file", "Incoming", "from @", "Posted a new status"]
    leaks = [f for f in forbidden if f in text]
    ok = "build_generic_push" in text and not leaks
    return ProofCheck(
        name="push_generic",
        passed=ok,
        detail="push.py uses build_generic_push" if ok else f"leaks or missing builder: {leaks}",
    )


def _check_enforcement_files() -> List[ProofCheck]:
    checks: List[ProofCheck] = []
    for rel in ENFORCEMENT_PATHS:
        path = REPO_ROOT / rel
        checks.append(
            ProofCheck(
                name=f"file:{rel}",
                passed=path.is_file(),
                detail="" if path.is_file() else "missing",
            )
        )
    return checks


def _check_gate_artifacts() -> List[ProofCheck]:
    checks: List[ProofCheck] = []
    for rel in ENGINE4_UNIT_MODULES + ENGINE4_INTEGRATION_MODULES + ENGINE4_SCRIPTS:
        path = BACKEND_ROOT / rel
        checks.append(
            ProofCheck(
                name=f"artifact:{rel}",
                passed=path.is_file(),
                detail="" if path.is_file() else "missing",
            )
        )
    return checks


def _check_charter_gate_documentation() -> ProofCheck:
    charter = REPO_ROOT / "memory" / "METADATA_MINIMIZATION_CHARTER.md"
    if not charter.is_file():
        return ProofCheck(name="charter_gate_docs", passed=False, detail="charter missing")
    text = charter.read_text(encoding="utf-8")
    ok = "**4.7**" in text and "run_engine4_gate.py" in text
    return ProofCheck(
        name="charter_gate_docs",
        passed=ok,
        detail="charter documents step 4.7 gate" if ok else "charter missing 4.7 / run_engine4_gate.py",
    )


def run_metadata_proof() -> MetadataProofReport:
    report = MetadataProofReport()
    report.checks.append(_check_engine3_prerequisite())
    report.checks.append(_check_engine4_steps())
    report.checks.append(_check_engine4_complete_helper())
    report.checks.append(_check_engine4_gaps())
    report.checks.append(_check_push_generic_enforcement())
    report.checks.extend(_check_enforcement_files())
    report.checks.extend(_check_gate_artifacts())
    report.checks.append(_check_charter_gate_documentation())
    return report