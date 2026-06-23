"""
SSC Metadata Minimization Policy — machine-readable mirror of memory/METADATA_MINIMIZATION_CHARTER.md.

Engine 4 Step 4.1: policy definition only.
Steps 4.2–4.7: enforcement code must align with this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from core.client_footprint_policy import engine3_complete

# last_seen controls (Engine 4.2–4.3)
LAST_SEEN_WRITE_INTERVAL_SEC = 300          # throttle DB writes to 5 minutes
LAST_SEEN_ONLINE_WINDOW_SEC = 300           # peers see online flag, not exact timestamp
LAST_SEEN_STORAGE_TTL_DAYS = 7              # older than this → treat as unknown

# Push controls (Engine 4.4–4.5)
GENERIC_PUSH_TITLE = "SSC"
GENERIC_PUSH_BODY = "New activity"

# Contacts tradeoff (Engine 4.6) — persistent social graph accepted
CONTACTS_PERSISTENT = True
CONTACTS_ALLOWED_FIELDS = frozenset({
    "user_id", "contact_id", "blocked", "muted", "created_at",
})


class GapSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class MetadataSurface:
    surface_id: str
    collection_or_channel: str
    risk: str
    engine4_step: Optional[str]
    mitigation: str
    accepted_tradeoff: bool = False


@dataclass(frozen=True)
class MetadataGap:
    gap_id: str
    description: str
    severity: GapSeverity
    engine4_step: Optional[str]
    later_engine: Optional[str] = None
    resolved: bool = False


METADATA_SURFACES: Dict[str, MetadataSurface] = {
    "last_seen": MetadataSurface(
        surface_id="last_seen",
        collection_or_channel="users.last_seen",
        risk="Precise activity timestamps enable stalking",
        engine4_step="4.3",
        mitigation="Write throttle + 7d TTL + peer coarsening + online flag",
    ),
    "push_visible": MetadataSurface(
        surface_id="push_visible",
        collection_or_channel="FCM / Web Push notification tray",
        risk="Usernames and message-type hints visible to OS and Google",
        engine4_step="4.4",
        mitigation=f"Generic title/body: {GENERIC_PUSH_TITLE!r} / {GENERIC_PUSH_BODY!r}",
    ),
    "push_data": MetadataSurface(
        surface_id="push_data",
        collection_or_channel="FCM / Web Push data payload",
        risk="Routing metadata leaves your metal via third-party push",
        engine4_step="4.5",
        mitigation="Opaque ids only (conversation_id, type); no usernames or content hints",
        accepted_tradeoff=True,
    ),
    "contacts_graph": MetadataSurface(
        surface_id="contacts_graph",
        collection_or_channel="contacts",
        risk="Server knows who you know",
        engine4_step="4.6",
        mitigation="Persistent for app function + panic UX; documented tradeoff",
        accepted_tradeoff=True,
    ),
    "friend_requests": MetadataSurface(
        surface_id="friend_requests",
        collection_or_channel="friend_requests",
        risk="Pending request history",
        engine4_step=None,
        mitigation="TTL enforced in Engine 1.3",
    ),
}

METADATA_GAPS: List[MetadataGap] = [
    MetadataGap(
        "M1", "last_seen stored and exposed with full precision to peers", GapSeverity.HIGH, "4.3", resolved=True,
    ),
    MetadataGap(
        "M2", "Push notifications expose usernames and message-type hints", GapSeverity.HIGH, "4.4", resolved=True,
    ),
    MetadataGap(
        "M3", "Push data payloads include author_username and group_name", GapSeverity.MEDIUM, "4.5", resolved=True,
    ),
    MetadataGap(
        "M4", "Contacts graph is persistent server metadata", GapSeverity.MEDIUM, "4.6", resolved=False,
    ),
    MetadataGap(
        "M5", "Translation sends plaintext to server when enabled", GapSeverity.CRITICAL, None, "9", resolved=True,
    ),
    MetadataGap(
        "M6", "WebRTC signaling cleartext on server", GapSeverity.HIGH, None, "8", resolved=True,
    ),
]

ENGINE4_STEPS: List[Tuple[str, str, bool]] = [
    ("4.1", "Metadata Minimization Charter", True),
    ("4.2", "last_seen write throttling + storage TTL", True),
    ("4.3", "last_seen coarsening + online flag on API read", True),
    ("4.4", "Generic push notification payloads", True),
    ("4.5", "Push data payload minimization", True),
    ("4.6", "Contacts metadata tradeoff review", True),
    ("4.7", "Engine 4 test gate", True),
]

PUSH_ENFORCEMENT_MODULE = "backend/core/push_payload.py"
LAST_SEEN_MODULE = "backend/core/last_seen.py"


def engine4_complete() -> bool:
    return all(done for _, _, done in ENGINE4_STEPS)


def open_gaps() -> List[MetadataGap]:
    return [g for g in METADATA_GAPS if not g.resolved]


def gaps_for_step(step_id: str) -> List[MetadataGap]:
    return [g for g in METADATA_GAPS if g.engine4_step == step_id]


def accepted_tradeoffs() -> List[MetadataSurface]:
    return [s for s in METADATA_SURFACES.values() if s.accepted_tradeoff]