"""User profile and search routes."""
import re

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user
from core.contact_helpers import get_user_public
from core.database import db
from core.models import UpdateProfileIn
from core.utils import validate_username
from security import rate_limit_check

router = APIRouter()


@router.patch("/me")
async def update_me(body: UpdateProfileIn, current=Depends(get_current_user)):
    update = {}
    if body.username:
        err = validate_username(body.username)
        if err:
            raise HTTPException(400, err)
        if await db.users.find_one({"username": body.username, "user_id": {"$ne": current["user_id"]}}):
            raise HTTPException(409, "Username already taken")
        update["username"] = body.username
    if body.language:
        update["language"] = body.language
    if update:
        await db.users.update_one({"user_id": current["user_id"]}, {"$set": update})
    user = await db.users.find_one(
        {"user_id": current["user_id"]},
        {"_id": 0, "password_hash": 0, "totp_secret": 0, "totp_pending_secret": 0},
    )
    return user


@router.get("/search")
async def search_users(q: str, current=Depends(get_current_user)):
    if not rate_limit_check(f"search:{current['user_id']}", max_hits=20, window_sec=60):
        raise HTTPException(429, "Too many searches")
    if not q or len(q) < 2:
        return []
    cur = db.users.find(
        {"username": {"$regex": f"^{re.escape(q)}", "$options": "i"}, "user_id": {"$ne": current["user_id"]}},
        {"_id": 0, "user_id": 1, "username": 1, "language": 1, "avatar": 1, "public_key": 1},
    ).limit(20)
    return await cur.to_list(20)


@router.get("/{user_id}/public")
async def get_user_public_route(user_id: str, current=Depends(get_current_user)):
    u = await get_user_public(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u