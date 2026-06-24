"""
Engine 6 — push / own-metal evaluation policy.

Evaluation complete 2026-06-24. Migration runbook deferred post-investors.
See memory/ENGINE_6_CHARTER.md.
"""
from __future__ import annotations

from typing import List, Tuple

ENGINE6_STEPS: List[Tuple[str, str, bool]] = [
    ("6.1", "Push path evaluation (FCM + VAPID keep; self-host deferred)", True),
    ("6.2", "Own-metal Mongo evaluation (Atlas keep; deferred post-investors)", True),
    ("6.3", "Own-metal migration runbook", False),
]

PUSH_PATH_DECISIONS = {
    "fcm_android": "keep",
    "web_vapid": "keep",
    "unified_push_self_host": "deferred",
    "apns_direct": "deferred",
}

OWN_METAL_DECISIONS = {
    "mongodb": "deferred_post_investors",
    "redis": "keep_upstash",
    "api_compute": "keep_cloud_run",
    "firebase_aux": "keep",
}


def engine6_evaluation_complete() -> bool:
    return all(done for step_id, _, done in ENGINE6_STEPS if step_id in ("6.1", "6.2"))


def engine6_complete() -> bool:
    return all(done for _, _, done in ENGINE6_STEPS)