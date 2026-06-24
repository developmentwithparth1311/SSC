"""Seed second test user + mutual contact with raul1988. Run from backend/:
  venv\\Scripts\\python.exe scripts\\seed_test_friend.py
"""
import asyncio
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv

load_dotenv(BACKEND / ".env")

FRIEND_EMAIL = "testfriend@test.com"
FRIEND_USERNAME = "testfriend"
FRIEND_PASSWORD = "123456"
MAIN_USERNAME = "raul1988"


def run_node_crypto(password: str):
    script = r"""
const { webcrypto } = require('node:crypto');
const enc = new TextEncoder();
function b64(buf) { return Buffer.from(buf).toString('base64'); }
async function deriveKeyFromPassword(password, saltBytes) {
  const keyMaterial = await webcrypto.subtle.importKey(
    'raw', enc.encode(password), { name: 'PBKDF2' }, false, ['deriveKey']);
  return webcrypto.subtle.deriveKey(
    { name: 'PBKDF2', salt: saltBytes, iterations: 200000, hash: 'SHA-256' },
    keyMaterial, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
}
async function main() {
  const password = process.argv[2];
  const kp = await webcrypto.subtle.generateKey(
    { name: 'RSA-OAEP', modulusLength: 2048, publicExponent: new Uint8Array([1,0,1]), hash: 'SHA-256' },
    true, ['encrypt', 'decrypt']);
  const pub = await webcrypto.subtle.exportKey('jwk', kp.publicKey);
  const priv = await webcrypto.subtle.exportKey('jwk', kp.privateKey);
  const salt = webcrypto.getRandomValues(new Uint8Array(16));
  const iv = webcrypto.getRandomValues(new Uint8Array(12));
  const key = await deriveKeyFromPassword(password, salt);
  const ct = await webcrypto.subtle.encrypt(
    { name: 'AES-GCM', iv }, key, enc.encode(JSON.stringify(priv)));
  process.stdout.write(JSON.stringify({
    public_key: JSON.stringify(pub),
    encrypted_private_key: b64(ct) + '.' + b64(iv),
    pk_salt: b64(salt),
  }));
}
main();
"""
    result = subprocess.run(
        ["node", "-e", script, password],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


async def main():
    import certifi
    from motor.motor_asyncio import AsyncIOMotorClient

    from core.auth import hash_password

    mongo_url = os.environ.get("MONGO_URL", "")
    db_name = os.environ.get("DB_NAME", "ssc")
    if not mongo_url:
        raise SystemExit("MONGO_URL not set in backend/.env")

    try:
        client = AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where())
    except Exception:
        client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    main_user = await db.users.find_one({"username": MAIN_USERNAME})
    if not main_user:
        raise SystemExit(f"Main user @{MAIN_USERNAME} not found — run seed_test_user.py first")

    from core.contact_graph import remove_mutual_contact

    old_friend = await db.users.find_one({"username": FRIEND_USERNAME})
    if old_friend:
        fid = old_friend["user_id"]
        await remove_mutual_contact(main_user["user_id"], fid)
    await db.users.delete_many({"$or": [{"email": FRIEND_EMAIL}, {"username": FRIEND_USERNAME}]})

    print("Generating encryption keys for testfriend…")
    keys = run_node_crypto(FRIEND_PASSWORD)

    friend_id = f"u_{uuid.uuid4().hex[:14]}"
    friend_doc = {
        "user_id": friend_id,
        "email": FRIEND_EMAIL,
        "username": FRIEND_USERNAME,
        "password_hash": hash_password(FRIEND_PASSWORD),
        "language": "en",
        "public_key": keys["public_key"],
        "encrypted_private_key": keys["encrypted_private_key"],
        "pk_salt": keys["pk_salt"],
        "avatar": None,
        "auth_provider": "password",
        "totp_enabled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(friend_doc)

    from core.contact_graph import establish_mutual_contact

    now = datetime.now(timezone.utc).isoformat()
    await establish_mutual_contact(main_user["user_id"], friend_id, created_at=now)

    client.close()

    print("Second test account ready:")
    print(f"  Username: {FRIEND_USERNAME}")
    print(f"  Password: {FRIEND_PASSWORD}")
    print(f"  Mutual contact with @{MAIN_USERNAME}")
    print("  Use testfriend to send messages / trigger push to your phone.")


if __name__ == "__main__":
    asyncio.run(main())