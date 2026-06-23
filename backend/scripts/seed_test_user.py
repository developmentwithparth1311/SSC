"""Seed test user with real E2E key material. Run from backend/: venv\\Scripts\\python.exe scripts/seed_test_user.py"""
import asyncio
import json
import os
import secrets
import subprocess
import sys
import uuid
from base64 import b64encode
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv

load_dotenv(BACKEND / ".env")

EMAIL = "raul1988@test.com"
USERNAME = "raul1988"
PASSWORD = "123456"


def run_node_crypto():
    """Generate RSA keys + password wrap via Node WebCrypto (matches browser exactly)."""
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
        ["node", "-e", script, PASSWORD],
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

    print("Generating encryption keys (Node WebCrypto)…")
    keys = run_node_crypto()

    try:
        client = AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where())
    except Exception:
        client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    await db.users.delete_many({"$or": [{"email": EMAIL}, {"username": USERNAME}]})

    user_id = f"u_{uuid.uuid4().hex[:14]}"
    doc = {
        "user_id": user_id,
        "email": EMAIL,
        "username": USERNAME,
        "password_hash": hash_password(PASSWORD),
        "language": "en",
        "public_key": keys["public_key"],
        "encrypted_private_key": keys["encrypted_private_key"],
        "pk_salt": keys["pk_salt"],
        "avatar": None,
        "auth_provider": "password",
        "totp_enabled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(doc)
    client.close()

    print("Test account ready:")
    print(f"  Email:    {EMAIL}")
    print(f"  Username: {USERNAME}")
    print(f"  Password: {PASSWORD}")
    print("  Login at http://localhost:3000/login")


if __name__ == "__main__":
    asyncio.run(main())