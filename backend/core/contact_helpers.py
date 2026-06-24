"""Contact and conversation permission helpers."""
from typing import Optional

from core.contact_graph import are_contacts as graph_are_contacts
from core.contact_graph import get_mutual_contact_ids as graph_mutual_ids
from core.database import db


async def get_user_public(user_id: str) -> Optional[dict]:
    return await db.users.find_one(
        {"user_id": user_id},
        {"_id": 0, "user_id": 1, "username": 1, "language": 1, "public_key": 1, "avatar": 1, "created_at": 1},
    )


async def are_contacts(user_a: str, user_b: str) -> bool:
    return await graph_are_contacts(user_a, user_b)


async def get_mutual_contact_ids(user_id: str) -> list[str]:
    return await graph_mutual_ids(user_id)


async def has_shared_conv(user_a: str, user_b: str) -> bool:
    if user_a == user_b:
        return True
    return bool(await db.conversations.find_one({"participants": {"$all": [user_a, user_b]}}))