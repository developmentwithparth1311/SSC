"""Issue JWT + Mongo session + HttpOnly cookie — Engine 5 Step 5.2."""
from __future__ import annotations

from fastapi import Request, Response

from core.auth import make_jwt, store_user_session
from core.session_cookie import set_session_cookie


async def create_session_token(user_id: str) -> str:
    token = make_jwt(user_id)
    await store_user_session(user_id, token)
    return token


async def issue_authenticated_session(
    response: Response,
    request: Request,
    user_id: str,
) -> str:
    token = await create_session_token(user_id)
    set_session_cookie(response, token, request)
    return token