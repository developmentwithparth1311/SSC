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
        {"attachment_id": file_id},
        {"_id": 1, "author_id": 1, "protocol": 1, "encrypted_keys": 1},
    )
    if not status:
        return False
    proto = (status.get("protocol") or "legacy_rsa").strip().lower()
    if proto == "signal_status_v1":
        from core.contact_helpers import are_contacts
        return await are_contacts(user_id, status.get("author_id", ""))
    return user_id in (status.get("encrypted_keys") or {})