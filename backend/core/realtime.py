"""WebSocket manager and conversation broadcast."""
import push as push_module
from ws import ConnectionManager

from core.database import db

manager = ConnectionManager()
push_module.manager = manager


async def broadcast_to_conversation(conversation_id: str, payload: dict):
    conv = await db.conversations.find_one({"conversation_id": conversation_id}, {"_id": 0})
    if not conv:
        return
    for uid in conv["participants"]:
        await manager.send_to_user(uid, payload)