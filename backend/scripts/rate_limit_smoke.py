"""Smoke test for abuse-defense rate limits (Task L.4).

Verifies:
- friend request burst limiter
- group creation limiter
- file upload burst limiter
"""
from __future__ import annotations

import asyncio
import json
import secrets
from dataclasses import asdict, dataclass

import httpx

BASE_URL = "http://127.0.0.1:8000/api"


@dataclass
class SmokeResult:
    register_ok: bool = False
    mutual_contact_ok: bool = False
    friend_request_limit_ok: bool = False
    group_create_limit_ok: bool = False
    file_upload_limit_ok: bool = False

    @property
    def passed(self) -> bool:
        return all(asdict(self).values())


async def _register(client: httpx.AsyncClient, tag: str) -> dict:
    suffix = secrets.token_hex(4)
    email = f"{tag}-{suffix}@example.com"
    username = f"{tag[0]}{suffix[:7]}"
    payload = {
        "email": email,
        "password": "SmokePass123!",
        "username": username,
        "public_key": f"pk-{tag}",
        "encrypted_private_key": f"epk-{tag}",
        "pk_salt": f"salt-{tag}",
        "language": "en",
    }
    spoof_ip = f"10.0.{secrets.randbelow(200)}.{secrets.randbelow(200)}"
    res = await client.post(
        f"{BASE_URL}/auth/register",
        json=payload,
        headers={"x-forwarded-for": spoof_ip},
    )
    if res.status_code >= 400:
        raise RuntimeError(f"register {tag} failed: {res.status_code} {res.text}")
    body = res.json()
    token = body.get("token")
    user = body.get("user") or {}
    if not token or not user.get("username"):
        raise RuntimeError(f"register {tag} missing token/user")
    return {"token": token, "username": user["username"]}


async def run() -> SmokeResult:
    result = SmokeResult()

    async with httpx.AsyncClient(timeout=20.0) as client:
        a = await _register(client, "alpha")
        b = await _register(client, "beta")
        result.register_ok = True

        # Establish mutual contacts (A -> B pending, then B accepts).
        req = await client.post(
            f"{BASE_URL}/contacts/request",
            headers={"Authorization": f"Bearer {a['token']}"},
            json={"username": b["username"]},
        )
        req.raise_for_status()
        req_id = req.json().get("request_id")
        if not req_id:
            raise RuntimeError("friend request did not return request_id")

        accept = await client.post(
            f"{BASE_URL}/contacts/requests/accept",
            headers={"Authorization": f"Bearer {b['token']}"},
            json={"request_id": req_id},
        )
        accept.raise_for_status()
        result.mutual_contact_ok = True

        # Friend request burst limit (send repeatedly to same target; limiter runs before pending check).
        friend_limited = False
        for _ in range(8):
            fr = await client.post(
                f"{BASE_URL}/contacts/request",
                headers={"Authorization": f"Bearer {a['token']}"},
                json={"username": b["username"]},
            )
            if fr.status_code == 429:
                friend_limited = True
                break
        result.friend_request_limit_ok = friend_limited

        # Group create limiter (max 4 / 10 min).
        group_limited = False
        for _ in range(7):
            grp = await client.post(
                f"{BASE_URL}/conversations",
                headers={"Authorization": f"Bearer {a['token']}"},
                json={
                    "is_group": True,
                    "peer_usernames": [b["username"]],
                    "name": "rl-smoke",
                },
            )
            if grp.status_code == 429:
                group_limited = True
                break
            if grp.status_code >= 400:
                raise RuntimeError(f"group create failed: {grp.status_code} {grp.text}")
        result.group_create_limit_ok = group_limited

        # File upload limiter burst (max 4 / 60 sec).
        file_limited = False
        for i in range(7):
            files = {
                "file": (f"smoke-{i}.bin", b"cipherblob", "application/octet-stream"),
            }
            data = {
                "encrypted": "true",
                "original_content_type": "application/octet-stream",
            }
            up = await client.post(
                f"{BASE_URL}/files/upload",
                headers={"Authorization": f"Bearer {a['token']}"},
                files=files,
                data=data,
            )
            if up.status_code == 429:
                file_limited = True
                break
            if up.status_code >= 400:
                raise RuntimeError(f"file upload failed: {up.status_code} {up.text}")
        result.file_upload_limit_ok = file_limited

    return result


def main() -> int:
    res = asyncio.run(run())
    payload = {**asdict(res), "passed": res.passed}
    print(json.dumps(payload, indent=2))
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
