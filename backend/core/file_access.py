"""File download authorization — owner or shared via message/status only."""
from core.database import db


async def user_can_access_file(user_id: str, file_id: str, owner_id: str) -> bool:
    if user_id == owner_id:
        return True
    msg = await db.messages.find_one({"attachment_id": file_id}, {"conversation_id": 1})
    if msg:
        conv = await db.conversations.find_one(
            {"conversation_id": msg["conversation_id"], "participants": user_id},
            {"_id": 1},
        )
        if conv:
            return True
    status = await db.statuses.find_one(
        {f"encrypted_keys.{user_id}": {"$exists": True}, "attachment_id": file_id},
        {"_id": 1},
    )
    return bool(status)