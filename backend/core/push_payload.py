"""Generic push notification payloads — Engine 4 Steps 4.4–4.5."""
from __future__ import annotations

from typing import Any, Dict, Optional

from core.metadata_policy import GENERIC_PUSH_BODY, GENERIC_PUSH_TITLE

# Activity types — routing only; never shown in notification title/body.
ACTIVITY_MESSAGE = "message"
ACTIVITY_CALL = "call"
ACTIVITY_FRIEND_REQUEST = "friend_request"
ACTIVITY_FRIEND_ACCEPT = "friend_accept"
ACTIVITY_STATUS = "status"
ACTIVITY_GROUP_EVENT = "group_event"

# Keys allowed in FCM/web-push data payloads (opaque routing — no usernames or content hints).
ALLOWED_DATA_KEYS = frozenset({
    "type",
    "conversation_id",
    "mode",
    "from",
    "group",
    "tag",
    "silent",
})


def build_generic_push(
    activity_type: str,
    *,
    conversation_id: Optional[str] = None,
    tag: Optional[str] = None,
    silent: bool = False,
    extra_data: Optional[Dict[str, Any]] = None,
    vibrate: Optional[list] = None,
    renotify: bool = True,
) -> dict:
    """
    Visible notification is always generic. Data carries minimal opaque routing ids only.
    """
    data: Dict[str, str] = {"type": activity_type}
    if conversation_id:
        data["conversation_id"] = conversation_id
    if extra_data:
        for key, val in extra_data.items():
            if key not in ALLOWED_DATA_KEYS or val is None:
                continue
            if isinstance(val, bool):
                data[key] = "1" if val else "0"
            else:
                data[key] = str(val)

    payload: dict = {
        "title": GENERIC_PUSH_TITLE,
        "body": GENERIC_PUSH_BODY,
        "type": activity_type,
        "tag": tag or f"ssc-{activity_type}",
        "data": data,
        "silent": silent,
        "renotify": renotify,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if vibrate:
        payload["vibrate"] = vibrate
    return payload


def sanitize_push_data(data: dict) -> Dict[str, str]:
    """Strip disallowed keys before third-party push egress."""
    if not isinstance(data, dict):
        return {"type": ACTIVITY_MESSAGE}
    out: Dict[str, str] = {}
    for key, val in data.items():
        if key not in ALLOWED_DATA_KEYS or val is None:
            continue
        if isinstance(val, bool):
            out[key] = "1" if val else "0"
        else:
            out[key] = str(val)
    if "type" not in out:
        out["type"] = ACTIVITY_MESSAGE
    return out