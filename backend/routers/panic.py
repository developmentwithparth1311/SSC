"""Panic wipe route — erases local data footprint, keeps the account."""
from fastapi import APIRouter, Depends

from core.auth import get_current_user
from core.database import db
from core.files import delete_file_gridfs
from core.logging_config import logger

router = APIRouter()


@router.post("/panic-wipe")
async def panic_wipe(current=Depends(get_current_user)):
    uid = current["user_id"]
    logger.warning(f"panic-wipe executed for user={uid}")

    convs = await db.conversations.find({"participants": uid}, {"_id": 0, "conversation_id": 1}).to_list(1000)
    conv_ids = [c["conversation_id"] for c in convs]
    if conv_ids:
        await db.messages.delete_many({"conversation_id": {"$in": conv_ids}})
        await db.conversations.delete_many({"conversation_id": {"$in": conv_ids}})

    files = await db.files.find({"owner_id": uid, "is_deleted": False}).to_list(1000)
    for f in files:
        try:
            await delete_file_gridfs(f["file_id"])
        except Exception as e:
            logger.warning(f"panic-wipe gridfs delete failed file={f.get('file_id')}: {e}")
    await db.files.update_many({"owner_id": uid}, {"$set": {"is_deleted": True}})

    await db.statuses.delete_many({"author_id": uid})
    await db.message_reads.delete_many({"user_id": uid})
    await db.user_sessions.delete_many({"user_id": uid})
    await db.push_subscriptions.delete_many({"user_id": uid})
    await db.native_push_tokens.delete_many({"user_id": uid})

    return {"ok": True, "wiped_conversations": len(conv_ids), "wiped_files": len(files)}