"""Run one retention janitor cycle and print summary.

Usage:
  venv\\Scripts\\python.exe scripts\\retention_janitor.py
  venv\\Scripts\\python.exe scripts\\retention_janitor.py --json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from core.config import DB_NAME, MONGO_URL  # noqa: E402
from core.retention_janitor import run_retention_janitor_once_with_handles  # noqa: E402


async def _main(args: argparse.Namespace) -> int:
    if MONGO_URL.startswith("mongodb+srv://") or "tls=true" in MONGO_URL:
        import certifi

        client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
    else:
        client = AsyncIOMotorClient(MONGO_URL)
    database = client[DB_NAME]
    gridfs_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="ssc_files")

    try:
        await database.command("ping")
    except Exception as exc:
        print(f"FAIL: MongoDB ping failed: {type(exc).__name__}: {exc}")
        client.close()
        return 1

    report = await run_retention_janitor_once_with_handles(database, gridfs_bucket)
    payload = report.to_dict()

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Retention janitor — database: {DB_NAME}")
        for key, value in payload.items():
            print(f"{key}: {value}")

    client.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SSC retention janitor single run")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()
    return asyncio.run(_main(args))


if __name__ == "__main__":
    raise SystemExit(main())
