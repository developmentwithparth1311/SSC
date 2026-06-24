"""
Contacts graph privacy policy — server-blind friend graph.

See memory/CONTACT_GRAPH_PRIVACY_CHARTER.md.
"""
from __future__ import annotations

from typing import List, Tuple

LEGACY_CONTACTS_COLLECTION = "contacts"
BLIND_COLLECTIONS: Tuple[str, ...] = (
    "contact_seals",
    "contact_blocks",
    "contact_mutes",
    "contact_rosters",
)

CONTACTS_GRAPH_STEPS: List[Tuple[str, str, bool]] = [
    ("CG.1", "Charter + contact_graph module + gate", True),
    ("CG.2", "Seal-based are_contacts ACL", True),
    ("CG.3", "Legacy contacts migration on startup", True),
    ("CG.4", "Push/native mute via mute seals", True),
    ("CG.5", "Metadata gap M4 resolved", True),
]


def contacts_graph_privacy_complete() -> bool:
    return all(done for _, _, done in CONTACTS_GRAPH_STEPS)