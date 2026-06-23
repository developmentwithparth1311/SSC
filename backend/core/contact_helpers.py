"""Contact and conversation permission helpers."""
from typing import Optional

from core.database import db


async def get_user_public(user_id: str) -> Optional[dict]:
    return await db.users.find_one(
        {"user_id": user_id},
        {"_id": 0, "user_id": 1, "username": 1, "language": 1, "public_key": 1, "avatar": 1, "created_at": 1},
    )


async def are_contacts(user_a: str, user_b: str) -> bool:
    if user_a == user_b:
        return True
    contact_ab = await db.contacts.find_one({"user_id": user_a, "contact_id": user_b})
    contact_ba = await db.contacts.find_one({"user_id": user_b, "contact_id": user_a})
    if not contact_ab or not contact_ba:
        return False
    if contact_ab.get("blocked") or contact_ba.get("blocked"):
        return False
    return True


async def has_shared_conv(user_a: str, user_b: str) -> bool:
    if user_a == user_b:
        return True
    return bool(await db.conversations.find_one({"participants": {"$all": [user_a, user_b]}}))