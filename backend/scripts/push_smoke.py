"""
Push notification smoke test.

1. Checks Firebase + native push tokens for target user (raul1988)
2. Logs in as testfriend and sends a message (triggers FCM when target is offline)

Run (backend must be up on port 8000):
  venv\\Scripts\\python.exe scripts\\push_smoke.py

Phone test: install latest APK, login as raul1988, allow notifications,
put app in background, then run this script.
"""
import asyncio
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

BASE = os.environ.get("SSC_API_BASE", "http://127.0.0.1:8000").rstrip("/")
API = f"{BASE}/api"

TARGET_USERNAME = "raul1988"
SENDER_USERNAME = "testfriend"
SENDER_PASSWORD = "123456"


def login(username: str, password: str) -> tuple[str, dict]:
    r = requests.post(
        f"{API}/auth/login",
        json={"email": username, "password": password},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    return body["token"], body["user"]


async def check_tokens(target_user_id: str) -> list:
    import certifi
    from motor.motor_asyncio import AsyncIOMotorClient

    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ.get("DB_NAME", "ssc")
    try:
        client = AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where())
    except Exception:
        client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    tokens = await db.native_push_tokens.find(
        {"user_id": target_user_id}, {"_id": 0, "token": 1, "platform": 1}
    ).to_list(20)
    client.close()
    return tokens


async def send_direct_fcm(token: str) -> bool:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    import native_push
    if not native_push.is_configured():
        return False
    from firebase_admin import messaging

    msg = messaging.Message(
        notification=messaging.Notification(
            title="SSC Push Test",
            body="Direct FCM test — push pipeline works!",
        ),
        data={
            "type": "message",
            "title": "SSC Push Test",
            "body": "Direct FCM test",
            "conversation_id": "push-smoke",
            "silent": "0",
        },
        token=token,
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(channel_id="ssc_messages"),
        ),
    )
    messaging.send(msg)
    return True


def send_message(token: str, sender: dict, target: dict) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{API}/conversations",
        json={"peer_username": target["username"]},
        headers=headers,
        timeout=15,
    )
    assert r.status_code == 200, r.text
    conv_id = r.json()["conversation_id"]
    msg = {
        "conversation_id": conv_id,
        "ciphertext": "cHVzaF9zbW9rZQ==",
        "iv": "aXY=",
        "encrypted_keys": {sender["user_id"]: "Aw==", target["user_id"]: "Bw=="},
        "message_type": "text",
        "plaintext_length": 10,
    }
    r2 = requests.post(f"{API}/messages", json=msg, headers=headers, timeout=15)
    assert r2.status_code == 200, r2.text
    return conv_id


async def main_async():
    print(f"Push smoke -> {API}\n")

    r = requests.get(f"{API}/push/public-key", timeout=10)
    assert r.status_code == 200, r.text
    info = r.json()
    print(f"  Native push enabled: {info.get('native_push_enabled')}")
    if not info.get("native_push_enabled"):
        print("  FAIL: Firebase not configured (check GOOGLE_APPLICATION_CREDENTIALS)")
        return 1

    _, target = login(TARGET_USERNAME, "123456")
    tokens = await check_tokens(target["user_id"])
    print(f"  FCM tokens for @{TARGET_USERNAME}: {len(tokens)}")
    if not tokens:
        print("\n  NO TOKENS — phone has not registered for push yet.")
        print("  Fix: install latest SSC-app-debug.apk, login, allow notifications.")
        return 1
    for t in tokens:
        print(f"    - {t.get('platform')} …{t.get('token', '')[-12:]}")

    token, sender = login(SENDER_USERNAME, SENDER_PASSWORD)
    print(f"\n  Sending test message from @{SENDER_USERNAME} -> @{TARGET_USERNAME}…")
    conv_id = send_message(token, sender, target)
    print(f"  OK message sent (conversation {conv_id})")
    print("  (Push only fires when @{TARGET} app is in background / not connected via WebSocket)")

    print("\n  Sending direct FCM test notification…")
    try:
        await send_direct_fcm(tokens[0]["token"])
        print("  OK direct FCM sent — check your phone notification tray!")
    except Exception as e:
        print(f"  WARN direct FCM failed: {e}")
        print("  Message-based push may still work when app is backgrounded.")

    print("\nDone.")
    return 0


def main():
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())