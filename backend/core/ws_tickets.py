"""Short-lived WebSocket tickets (avoid JWT in query strings)."""
import secrets
from typing import Optional

from security import _redis

_TICKET_TTL_SEC = 60
_MEM: dict[str, str] = {}


def _redis_key(ticket: str) -> str:
    return f"ssc:ws_ticket:{ticket}"


def issue_ws_ticket(user_id: str) -> str:
    ticket = secrets.token_urlsafe(24)
    if _redis:
        try:
            _redis.setex(_redis_key(ticket), _TICKET_TTL_SEC, user_id)
            return ticket
        except Exception:
            pass
    _MEM[ticket] = user_id
    return ticket


def consume_ws_ticket(ticket: str) -> Optional[str]:
    if not ticket:
        return None
    if _redis:
        try:
            key = _redis_key(ticket)
            user_id = _redis.get(key)
            if user_id:
                _redis.delete(key)
                return user_id
        except Exception:
            pass
    return _MEM.pop(ticket, None)