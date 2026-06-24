"""
Wipe ALL user data from MongoDB — empty database for fresh installed-app testing.

Deletes every user and all chat, contacts, Signal bundles, sessions, files, etc.
Does NOT drop indexes. Run only when you intend a full reset.

  venv\\Scripts\\python.exe scripts\\wipe_all_user_data.py --dry-run
  venv\\Scripts\\python.exe scripts\\wipe_all_user_data.py --confirm
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv

load_dotenv(BACKEND / ".env")

from core.config import DB_NAME, MONGO_URL  # noqa: E402
import core.database as database_module  # noqa: E402
import core.files as files_module  # noqa: E402
from core.files import delete_file_gridfs  # noqa: E402
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket  # noqa: E402

WIPE_COLLECTIONS = (
    "messages",
    "message_reads",
    "conversations",
    "statuses",
    "calls",
    "friend_requests",
    "contact_rosters",
    "contact_seals",
    "contact_blocks",
    "contact_mutes",
    "contacts",
    "signal_prekey_bundles",
    "user_sessions",
    "push_subscriptions",
    "native_push_tokens",
    "files",
    "users",
)


def _make_db():
    try:
        import certifi
        client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
    except Exception:
        client = AsyncIOMotorClient(MONGO_URL)
    database = client[DB_NAME]
    return client, database, AsyncIOMotorGridFSBucket(database, bucket_name="ssc_files")


async def _wipe_gridfs(db) -> int:
    count = 0
    cursor = db.files.find({"is_deleted": {"$ne": True}}, {"_id": 0, "file_id": 1})
    async for rec in cursor:
        fid = rec.get("file_id")
        if not fid:
            continue
        try:
            await delete_file_gridfs(fid)
            await db.files.update_one({"file_id": fid}, {"$set": {"is_deleted": True}})
            count += 1
        except Exception:
            pass
    return count


async def run(*, dry_run: bool, confirm: bool) -> int:
    if not dry_run and not confirm:
        print("Refusing to wipe without --confirm (or use --dry-run).")
        return 1

    client, db, grid_fs = _make_db()
    database_module.db = db
    database_module.grid_fs = grid_fs
    files_module.grid_fs = grid_fs

    users = await db.users.find({}, {"_id": 0, "username": 1, "email": 1}).to_list(100_000)
    print(f"{'DRY RUN — ' if dry_run else ''}Users to remove: {len(users)}")
    for u in users:
        print(f"  - @{u.get('username') or '(none)'} ({u.get('email') or ''})")

    counts = {}
    for name in WIPE_COLLECTIONS:
        counts[name] = await db[name].count_documents({})

    print("\nCollection counts:")
    for name in WIPE_COLLECTIONS:
        print(f"  {name}: {counts[name]}")

    if dry_run:
        print("\nDry run complete — no data deleted.")
        client.close()
        return 0

    grid_deleted = await _wipe_gridfs(db)
    print(f"\nGridFS files removed: {grid_deleted}")

    for name in WIPE_COLLECTIONS:
        if counts[name] == 0:
            continue
        r = await db[name].delete_many({})
        print(f"  deleted {name}: {r.deleted_count}")

    remaining = await db.users.count_documents({})
    print(f"\nDone. Remaining users: {remaining}")
    client.close()
    return 0 if remaining == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Wipe all SSC user data from MongoDB")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm", action="store_true", help="Required to actually delete")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(dry_run=args.dry_run, confirm=args.confirm)))


if __name__ == "__main__":
    main()