"""
SSC Session Hardening Policy — machine-readable mirror of memory/SESSION_HARDENING_CHARTER.md.

Engine 5 Step 5.1: policy definition only.
Steps 5.2–5.7: enforcement code must align with this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from core.metadata_policy import engine4_complete

# Session cookie (web — step 5.2)
SESSION_COOKIE_NAME = "session_token"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_SAMESITE = "lax"
SESSION_JWT_TTL_DAYS = 7

# Legacy client key — must be fully removed by step 5.5
LEGACY_JWT_LOCAL_STORAGE_KEY = "ssc_token"

# Native push token — remains in localStorage until separate hardening
NATIVE_PUSH_TOKEN_KEY = "ssc_native_push_token"


class SessionPlatform(str, Enum):
    WEB = "web"
    NATIVE = "native"


class GapSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class SessionSurface:
    surface_id: str
    platform: SessionPlatform
    storage: str
    engine5_step: Optional[str]
    target: str
    notes: str = ""


@dataclass(frozen=True)
class SessionGap:
    gap_id: str
    description: str
    severity: GapSeverity
    engine5_step: Optional[str]
    resolved: bool = False


SESSION_SURFACES: Dict[str, SessionSurface] = {
    "web_cookie": SessionSurface(
        surface_id="web_cookie",
        platform=SessionPlatform.WEB,
        storage="HttpOnly cookie session_token",
        engine5_step="5.2",
        target="Set on login/register; Secure when HTTPS; cleared on logout",
    ),
    "web_local_storage_jwt": SessionSurface(
        surface_id="web_local_storage_jwt",
        platform=SessionPlatform.WEB,
        storage=f"localStorage.{LEGACY_JWT_LOCAL_STORAGE_KEY}",
        engine5_step="5.3",
        target="Removed — cookie auth only",
        notes="Closes footprint gap C8 for web.",
    ),
    "native_memory_jwt": SessionSurface(
        surface_id="native_memory_jwt",
        platform=SessionPlatform.NATIVE,
        storage="sessionStore (React memory) + nativeSessionStore (AES device wrap)",
        engine5_step="5.4",
        target="Bearer from memory at runtime; encrypted wrap at rest — never plaintext ssc_token",
        notes="TASK B: survive force-close; cleared on logout/panic.",
    ),
    "ws_ticket": SessionSurface(
        surface_id="ws_ticket",
        platform=SessionPlatform.WEB,
        storage="Redis ssc:ws_ticket:* (60s)",
        engine5_step=None,
        target="Unchanged — opaque short-lived ticket",
    ),
    "redis_revocation": SessionSurface(
        surface_id="redis_revocation",
        platform=SessionPlatform.WEB,
        storage="Redis ssc:revoked:*",
        engine5_step="5.6",
        target="Required when ENV=production",
    ),
}

SESSION_GAPS: List[SessionGap] = [
    SessionGap("C8", "JWT in localStorage (session hijack on grabbed device)", GapSeverity.HIGH, "5.5", resolved=True),
    SessionGap("S1", "session_token cookie supported but never set on login", GapSeverity.HIGH, "5.2", resolved=True),
    SessionGap("S2", "Redis revocation optional in development", GapSeverity.MEDIUM, "5.6", resolved=True),
    SessionGap(
        "S3", "Native session lost on app force-close", GapSeverity.LOW, "5.4",
        resolved=True,
    ),
]

ENGINE5_STEPS: List[Tuple[str, str, bool]] = [
    ("5.1", "Session Hardening Charter", True),
    ("5.2", "Backend HttpOnly session cookie", True),
    ("5.3", "Web client cookie auth (no localStorage JWT)", True),
    ("5.4", "Native in-memory session module", True),
    ("5.5", "Panic/logout/orchestrator + C8 closure", True),
    ("5.6", "Production Redis revocation gate + session TTL alignment", True),
    ("5.7", "Engine 5 test gate", True),
]

# Founder deployment intent (charter §2)
TESTING_STRATEGY = {
    "lan_localhost": "founder laptop dev preview only — not for external users",
    "real_testers": "Firebase App Distribution — smashmaxxx, raullavita1988, velvetnightshub @gmail.com",
    "domain_https": "deferred until ~2026-06-28",
    "no_lan_exposure": "tester APK must use production API URL at build time",
}


def engine5_complete() -> bool:
    return all(done for _, _, done in ENGINE5_STEPS)


def open_gaps() -> List[SessionGap]:
    return [g for g in SESSION_GAPS if not g.resolved]


def gaps_for_step(step_id: str) -> List[SessionGap]:
    return [g for g in SESSION_GAPS if g.engine5_step == step_id]


def engine5_prerequisite_met() -> bool:
    return engine4_complete()