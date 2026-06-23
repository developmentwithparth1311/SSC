"""HttpOnly session cookie helpers — Engine 5 Steps 5.2–5.5."""
from __future__ import annotations

from typing import Optional

from fastapi import Request, Response

from core.session_policy import (
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_PATH,
    SESSION_COOKIE_SAMESITE,
)
from core.session_ttl import session_ttl_seconds


def session_cookie_max_age() -> int:
    return session_ttl_seconds()


def cookie_secure(request: Request) -> bool:
    """Secure flag: always in production; also when request arrived over HTTPS."""
    from core.config import ENV

    if ENV == "production":
        return True
    return request.url.scheme == "https"


def set_session_cookie(response: Response, token: str, request: Request) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=session_cookie_max_age(),
        httponly=True,
        secure=cookie_secure(request),
        samesite=SESSION_COOKIE_SAMESITE,
        path=SESSION_COOKIE_PATH,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path=SESSION_COOKIE_PATH,
        samesite=SESSION_COOKIE_SAMESITE,
    )


def resolve_request_session_token(
    authorization: Optional[str],
    session_token: Optional[str],
) -> Optional[str]:
    """Bearer header takes precedence; else HttpOnly cookie (Engine 5.5)."""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return session_token