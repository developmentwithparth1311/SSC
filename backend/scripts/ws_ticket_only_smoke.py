"""Verify websocket ticket-only auth flow.

Checks:
1) Register/login user and request ws ticket.
2) WebSocket with ticket connects and receives connected event.
3) WebSocket with token query is rejected.
"""
from __future__ import annotations

import asyncio
import json
import secrets
from dataclasses import dataclass, asdict

import httpx
import websockets

BASE_URL = "http://127.0.0.1:8000/api"
WS_URL = "ws://127.0.0.1:8000/api/ws"


@dataclass
class SmokeResult:
    register_ok: bool = False
    ws_ticket_ok: bool = False
    ticket_connect_ok: bool = False
    token_query_rejected: bool = False

    @property
    def passed(self) -> bool:
        return all(asdict(self).values())


async def run() -> SmokeResult:
    result = SmokeResult()

    suffix = secrets.token_hex(4)
    email = f"ws-smoke-{suffix}@example.com"
    username = f"u{suffix[:7]}"
    password = "SmokePass123!"

    async with httpx.AsyncClient(timeout=15.0) as client:
        reg = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "username": username,
                "public_key": "pk-smoke",
                "encrypted_private_key": "epk-smoke",
                "pk_salt": "salt-smoke",
                "language": "en",
            },
        )
        if reg.status_code >= 400:
            raise RuntimeError(f"register failed status={reg.status_code} body={reg.text}")
        token = reg.json().get("token")
        if not token:
            raise RuntimeError("register did not return token")
        result.register_ok = True

        ticket_resp = await client.post(
            f"{BASE_URL}/auth/ws-ticket",
            headers={"Authorization": f"Bearer {token}"},
        )
        ticket_resp.raise_for_status()
        ticket = ticket_resp.json().get("ticket")
        if not ticket:
            raise RuntimeError("ws-ticket endpoint did not return ticket")
        result.ws_ticket_ok = True

    async with websockets.connect(f"{WS_URL}?ticket={ticket}") as ws_ticket:
        raw = await asyncio.wait_for(ws_ticket.recv(), timeout=10.0)
        data = json.loads(raw)
        if data.get("type") != "connected":
            raise RuntimeError("ticket websocket did not return connected")
        result.ticket_connect_ok = True

    try:
        async with websockets.connect(f"{WS_URL}?token={token}") as ws_token:
            await asyncio.wait_for(ws_token.recv(), timeout=5.0)
    except Exception:
        result.token_query_rejected = True

    return result


def main() -> int:
    res = asyncio.run(run())
    payload = {
        **asdict(res),
        "passed": res.passed,
    }
    print(json.dumps(payload, indent=2))
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
