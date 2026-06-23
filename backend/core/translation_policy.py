"""
Engine 9 — on-device translation policy (closes M5).

Server-side /api/translate remains disabled by default.
Android APK uses Google ML Kit on-device via SscTranslate Capacitor plugin.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Tuple

from core.translation_access import is_translation_allowed

REPO_ROOT = Path(__file__).resolve().parents[2]

ENGINE9_STEPS: List[Tuple[str, str, bool]] = [
    ("9.1", "On-device translation policy + client path", True),
    ("9.2", "ML Kit Capacitor plugin (Android)", True),
    ("9.3", "Message UI uses on-device translate (no server plaintext on APK)", True),
    ("9.4", "Engine 9 gate + M5 closed", True),
]

ENFORCEMENT_PATHS_91: Tuple[str, ...] = (
    "backend/core/translation_policy.py",
    "frontend/src/lib/translation/translateClient.js",
)

ENFORCEMENT_PATHS_92: Tuple[str, ...] = (
    "frontend/android/app/src/main/java/chat/ssc/secure/plugins/SscTranslatePlugin.java",
    "frontend/src/lib/translation/nativeTranslate.js",
)

ENFORCEMENT_PATHS_93: Tuple[str, ...] = (
    "frontend/src/components/Message.jsx",
)

ENGINE9_ALL_ENFORCEMENT_PATHS: Tuple[str, ...] = (
    *ENFORCEMENT_PATHS_91,
    *ENFORCEMENT_PATHS_92,
    *ENFORCEMENT_PATHS_93,
)


class TranslationMode(str, Enum):
    OFF = "off"
    ON_DEVICE = "on_device"
    SERVER = "server"


def engine9_complete() -> bool:
    return all(done for _, _, done in ENGINE9_STEPS)


def production_translation_mode() -> TranslationMode:
    """Production default: server off; clients use on-device when native."""
    if is_translation_allowed():
        return TranslationMode.SERVER
    return TranslationMode.ON_DEVICE


def m5_closed() -> bool:
    """M5 closed when on-device path ships and server translate stays off by default."""
    return engine9_complete() and not is_translation_allowed()


@dataclass(frozen=True)
class TranslationProofCheck:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class TranslationProofReport:
    checks: List[TranslationProofCheck]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


def run_translation_proof() -> TranslationProofReport:
    checks: List[TranslationProofCheck] = []

    missing = [p for p in ENGINE9_ALL_ENFORCEMENT_PATHS if not (REPO_ROOT / p).is_file()]
    checks.append(TranslationProofCheck(
        name="engine9_enforcement_paths",
        passed=not missing,
        detail="all Engine 9 paths present" if not missing else f"missing: {missing}",
    ))

    message = (REPO_ROOT / "frontend/src/components/Message.jsx").read_text(encoding="utf-8")
    server_translate_call = (
        "api.post('/translate'" in message
        or 'api.post("/translate"' in message
        or "api.post(`/translate`" in message
    )
    checks.append(TranslationProofCheck(
        name="engine9_message_uses_client",
        passed="translateMessageText" in message and not server_translate_call,
        detail="Message.jsx uses translateClient, not direct api.post('/translate')",
    ))

    gradle = (REPO_ROOT / "frontend/android/app/build.gradle").read_text(encoding="utf-8")
    checks.append(TranslationProofCheck(
        name="engine9_mlkit_dependency",
        passed="com.google.mlkit:translate" in gradle,
        detail="ML Kit translate dependency pinned in Android build",
    ))

    checks.append(TranslationProofCheck(
        name="engine9_m5_closed",
        passed=m5_closed(),
        detail="M5 closed — server translation off by default" if m5_closed() else "M5 open",
    ))

    checks.append(TranslationProofCheck(
        name="engine9_complete",
        passed=engine9_complete(),
        detail="all ENGINE9_STEPS marked done" if engine9_complete() else "incomplete steps",
    ))

    return TranslationProofReport(checks=checks)