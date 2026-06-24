"""
Delete disposable tester accounts from MongoDB.

Removes users matching:
  - username starting with e2e
  - username testfriend
  - email ending with @ssc.dev

Preserves founder / primary accounts (default: raul1988).

Run from backend/:
  venv\\Scripts\\python.exe scripts\\reset_tester_accounts.py
  venv\\Scripts\\python.exe scripts\\reset_tester_accounts.py --dry-run
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
import core.contact_graph as contact_graph_module  # noqa: E402
import core.database as database_module  # noqa: E402
import core.files as files_module  # noqa: E402
from core.contact_graph import (  # noqa: E402
    block_seal,
    mute_seal,
    pair_seal,
    remove_mutual_contact,
    seal_exists,
)
from core.files import delete_file_gridfs  # noqa: E402
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket  # noqa: E402

PRESERVE_USERNAMES = frozenset({"raul1988"})


def is_tester_user(doc: dict) -> bool:
    username = (doc.get("username") or "").lower()
    email = (doc.get("email") or "").lower()
    if username in PRESERVE_USERNAMES:
        return False
    if username.startswith("e2e"):
        return True
    if username == "testfriend":
        return True
    if email.endswith("@ssc.dev"):
        return True
    return False


def _make_db():
    try:
        import certifi
        client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
    except Exception:
        client = AsyncIOMotorClient(MONGO_URL)
    database = client[DB_NAME]
    return client, database, AsyncIOMotorGridFSBucket(database, bucket_name="ssc_files")


async def _delete_user_files(db, user_id: str) -> int:
    count = 0
    cursor = db.files.find({"owner_id": user_id, "is_deleted": False}, {"_id": 0, "file_id": 1})
    async for rec in cursor:
        fid = rec.get("file_id")
        if fid:
            await delete_file_gridfs(fid)
            await db.files.update_one({"file_id": fid}, {"$set": {"is_deleted": True}})
            count += 1
    return count


async def _purge_user_data(db, user_id: str) -> dict:
    convs = await db.conversations.find(
        {"participants": user_id},
        {"_id": 0, "conversation_id": 1},
    ).to_list(10_000)
    conv_ids = [c["conversation_id"] for c in convs if c.get("conversation_id")]

    attachment_ids = set()
    if conv_ids:
        cursor = db.messages.find(
            {"conversation_id": {"$in": conv_ids}, "attachment_id": {"$exists": True, "$ne": None}},
            {"_id": 0, "attachment_id": 1},
        )
        async for msg in cursor:
            if msg.get("attachment_id"):
                attachment_ids.add(msg["attachment_id"])

    status_cursor = db.statuses.find(
        {"author_id": user_id, "attachment_id": {"$exists": True, "$ne": None}},
        {"_id": 0, "attachment_id": 1},
    )
    async for st in status_cursor:
        if st.get("attachment_id"):
            attachment_ids.add(st["attachment_id"])

    for fid in attachment_ids:
        try:
            await delete_file_gridfs(fid)
            await db.files.update_one({"file_id": fid}, {"$set": {"is_deleted": True}})
        except Exception:
            pass

    stats = {
        "conversations": 0,
        "messages": 0,
        "message_reads": 0,
        "statuses": 0,
        "calls": 0,
        "sessions": 0,
        "push": 0,
        "native_push": 0,
        "files": 0,
        "contact_rosters": 0,
        "contact_seals": 0,
        "contact_blocks": 0,
        "contact_mutes": 0,
        "friend_requests": 0,
    }

    if conv_ids:
        r = await db.messages.delete_many({"conversation_id": {"$in": conv_ids}})
        stats["messages"] = r.deleted_count
        r = await db.message_reads.delete_many({"conversation_id": {"$in": conv_ids}})
        stats["message_reads"] += r.deleted_count
        r = await db.conversations.delete_many({"conversation_id": {"$in": conv_ids}})
        stats["conversations"] = r.deleted_count

    r = await db.message_reads.delete_many({"user_id": user_id})
    stats["message_reads"] += r.deleted_count
    r = await db.statuses.delete_many({"author_id": user_id})
    stats["statuses"] = r.deleted_count
    r = await db.calls.delete_many({"$or": [{"caller_id": user_id}, {"callee_id": user_id}]})
    stats["calls"] = r.deleted_count
    r = await db.user_sessions.delete_many({"user_id": user_id})
    stats["sessions"] = r.deleted_count
    r = await db.push_subscriptions.delete_many({"user_id": user_id})
    stats["push"] = r.deleted_count
    r = await db.native_push_tokens.delete_many({"user_id": user_id})
    stats["native_push"] = r.deleted_count
    stats["files"] = await _delete_user_files(db, user_id)

    r = await db.contact_rosters.delete_one({"user_id": user_id})
    stats["contact_rosters"] = r.deleted_count

    # Legacy collection if present
    try:
        await db.contacts.delete_many({"$or": [{"user_id": user_id}, {"contact_id": user_id}]})
    except Exception:
        pass

    r = await db.friend_requests.delete_many({
        "$or": [{"from_user_id": user_id}, {"to_user_id": user_id}],
    })
    stats["friend_requests"] = r.deleted_count

    return stats


async def _detach_from_preserved(db, deleted_id: str, preserved_ids: list[str], *, dry_run: bool) -> int:
    detached = 0
    for preserved_id in preserved_ids:
        if await seal_exists(preserved_id, deleted_id):
            if not dry_run:
                await remove_mutual_contact(preserved_id, deleted_id)
            detached += 1
    if not dry_run:
        # Remove orphan seals/blocks/mutes referencing deleted user with any known peer
        for peer_id in preserved_ids:
            await db.contact_seals.delete_one({"seal": pair_seal(deleted_id, peer_id)})
            await db.contact_blocks.delete_one({"seal": block_seal(deleted_id, peer_id)})
            await db.contact_blocks.delete_one({"seal": block_seal(peer_id, deleted_id)})
            await db.contact_mutes.delete_one({"seal": mute_seal(deleted_id, peer_id)})
            await db.contact_mutes.delete_one({"seal": mute_seal(peer_id, deleted_id)})
    return detached


async def run(*, dry_run: bool) -> int:
    client, db, grid_fs = _make_db()
    database_module.db = db
    database_module.grid_fs = grid_fs
    contact_graph_module.db = db
    files_module.grid_fs = grid_fs
    all_users = await db.users.find(
        {},
        {"_id": 0, "user_id": 1, "username": 1, "email": 1},
    ).to_list(50_000)

    testers = [u for u in all_users if is_tester_user(u)]
    preserved = [u for u in all_users if not is_tester_user(u)]
    preserved_ids = [u["user_id"] for u in preserved]

    if not testers:
        print("No tester accounts matched — nothing to do.")
        return 0

    print(f"{'DRY RUN — ' if dry_run else ''}Found {len(testers)} tester account(s) to remove:")
    for u in testers:
        print(f"  - @{u.get('username')} ({u.get('email')})")

    if dry_run:
        print(f"Would preserve {len(preserved)} account(s).")
        client.close()
        return 0

    try:
        for u in testers:
            uid = u["user_id"]
            print(f"\nPurging @{u.get('username')} …")
            detached = await _detach_from_preserved(db, uid, preserved_ids, dry_run=False)
            stats = await _purge_user_data(db, uid)
            r = await db.users.delete_one({"user_id": uid})
            stats["users"] = r.deleted_count
            print(f"  detached from {detached} preserved contact(s)")
            for key, val in stats.items():
                if val:
                    print(f"  {key}: {val}")

        print(f"\nDone. Preserved {len(preserved)} account(s).")
        return 0
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove disposable SSC tester accounts")
    parser.add_argument("--dry-run", action="store_true", help="List matches without deleting")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(dry_run=args.dry_run)))


if __name__ == "__main__":
    main()