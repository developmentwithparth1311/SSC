"""Engine 5 Step 5.2 — HttpOnly session cookie helpers."""
from unittest.mock import patch

from starlette.requests import Request
from starlette.responses import Response

from core.session_cookie import (
    clear_session_cookie,
    cookie_secure,
    session_cookie_max_age,
    set_session_cookie,
)
from core.session_policy import SESSION_COOKIE_NAME, SESSION_JWT_TTL_DAYS


def _request(scheme: str = "http") -> Request:
    scope = {
        "type": "http",
        "headers": [],
        "method": "POST",
        "scheme": scheme,
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 1234),
        "path": "/api/auth/login",
    }
    return Request(scope)


def _set_cookie_header(response: Response) -> str:
    for key, val in response.raw_headers:
        if key.decode().lower() == "set-cookie":
            return val.decode()
    return ""


def test_session_cookie_max_age_matches_jwt_ttl():
    assert session_cookie_max_age() == SESSION_JWT_TTL_DAYS * 86400


def test_cookie_secure_false_on_http_dev():
    with patch("core.config.ENV", "development"):
        assert cookie_secure(_request("http")) is False


def test_cookie_secure_true_in_production():
    with patch("core.config.ENV", "production"):
        assert cookie_secure(_request("http")) is True


def test_cookie_secure_true_on_https_dev():
    with patch("core.config.ENV", "development"):
        assert cookie_secure(_request("https")) is True


def test_set_session_cookie_httponly_and_path():
    response = Response()
    set_session_cookie(response, "tok_test", _request("http"))
    header = _set_cookie_header(response)
    assert SESSION_COOKIE_NAME in header
    assert "HttpOnly" in header
    assert "Path=/" in header
    assert "SameSite=lax" in header
    assert "tok_test" in header


def test_clear_session_cookie():
    response = Response()
    clear_session_cookie(response)
    header = _set_cookie_header(response)
    assert SESSION_COOKIE_NAME in header
    assert "Max-Age=0" in header or '=""' in header or "=;" in header


def test_auth_routes_use_session_issue():
    auth_src = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "routers"
        / "auth.py"
    ).read_text(encoding="utf-8")
    assert "issue_authenticated_session" in auth_src
    assert "clear_session_cookie" in auth_src
    assert 'Cookie(None)' in auth_src or "session_token" in auth_src