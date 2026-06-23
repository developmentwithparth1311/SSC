"""Panic wipe route — erases local data footprint, keeps the account."""
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Header, Response

from core.auth import get_current_user
from core.panic_wipe_service import execute_server_panic_wipe
from core.session_cookie import clear_session_cookie, resolve_request_session_token

router = APIRouter()


@router.post("/panic-wipe")
async def panic_wipe(
    response: Response,
    current=Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None),
):
    token = resolve_request_session_token(authorization, session_token)
    result = await execute_server_panic_wipe(current["user_id"], session_token=token)
    clear_session_cookie(response)
    return result