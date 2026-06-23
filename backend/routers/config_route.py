"""Public client configuration (ICE, Turnstile, VAPID)."""
from fastapi import APIRouter

import os

from core.config import (
    ENV,
    TRANSLATION_ENABLED,
    TURNSTILE_SITEKEY,
    TURN_CREDENTIAL,
    TURN_USERNAME,
    VAPID_PUBLIC,
)
from security import get_rate_limit_backend

router = APIRouter()


@router.get("/config")
async def public_config():
    if TURN_USERNAME and TURN_CREDENTIAL:
        ice_servers = [
            {"urls": "stun:stun.relay.metered.ca:80"},
            {"urls": "turn:global.relay.metered.ca:80", "username": TURN_USERNAME, "credential": TURN_CREDENTIAL},
            {"urls": "turn:global.relay.metered.ca:80?transport=tcp", "username": TURN_USERNAME, "credential": TURN_CREDENTIAL},
            {"urls": "turn:global.relay.metered.ca:443", "username": TURN_USERNAME, "credential": TURN_CREDENTIAL},
            {"urls": "turns:global.relay.metered.ca:443?transport=tcp", "username": TURN_USERNAME, "credential": TURN_CREDENTIAL},
        ]
    else:
        ice_servers = [
            {"urls": "stun:stun.l.google.com:19302"},
            {"urls": "stun:stun1.l.google.com:19302"},
            {"urls": "stun:stun2.l.google.com:19302"},
        ]
    return {
        "turnstile_sitekey": TURNSTILE_SITEKEY,
        "vapid_public_key": VAPID_PUBLIC,
        "app_name": "SSC",
        "version": "0.4-standalone",
        "env": ENV,
        "translation_enabled": TRANSLATION_ENABLED,
        "translation_provider": (os.environ.get("TRANSLATION_PROVIDER") or "mymemory").lower(),
        "rate_limit_backend": get_rate_limit_backend(),
        "ice_servers": ice_servers,
    }