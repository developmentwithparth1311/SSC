"""Engine 5 Step 5.3 — web client cookie auth (source enforcement)."""
from pathlib import Path

from core.google_auth import frontend_redirect
from core.session_policy import ENGINE5_STEPS

REPO = Path(__file__).resolve().parents[2]
FRONTEND = REPO / "frontend" / "src"


def test_engine5_step_5_3_marked_complete():
    done = {step_id: complete for step_id, _, complete in ENGINE5_STEPS}
    assert done["5.3"] is True


def test_session_store_module_exists():
    text = (FRONTEND / "lib" / "sessionStore.js").read_text(encoding="utf-8")
    assert "usesCookieAuth" in text
    assert "persistSessionToken" in text
    assert "purgeLegacyJwtFromStorage" in text
    assert "usesCookieAuth()" in text


def test_api_js_cookie_auth_on_web():
    text = (FRONTEND / "lib" / "api.js").read_text(encoding="utf-8")
    assert "withCredentials: usesCookieAuth()" in text
    assert "usesCookieAuth()" in text
    assert "localStorage.getItem('ssc_token')" not in text
    assert "localStorage.getItem(\"ssc_token\")" not in text


def test_auth_context_no_localstorage_jwt_on_web():
    text = (FRONTEND / "context" / "AuthContext.jsx").read_text(encoding="utf-8")
    assert "persistSessionToken" in text
    assert "localStorage.setItem('ssc_token'" not in text
    assert "purgeLegacyJwtFromStorage" in text


def test_google_callback_installed_uses_token_and_me():
    text = (FRONTEND / "pages" / "GoogleAuthCallback.jsx").read_text(encoding="utf-8")
    assert "isInstalledClient()" in text
    assert "/auth/me" in text
    assert "persistSessionToken" in text
    assert "localStorage.setItem('ssc_token'" not in text


def test_orchestrator_cookie_logout_on_web():
    text = (FRONTEND / "lib" / "clientFootprintOrchestrator.js").read_text(encoding="utf-8")
    assert "usesBearerAuth" in text


def test_google_native_redirect_uses_capacitor_origin():
    url = frontend_redirect("native", "tok", False)
    assert url.startswith("https://localhost/auth/google")


def test_google_native_redirect_keeps_token():
    url = frontend_redirect("native", "native_tok", True)
    assert "token=native_tok" in url
    assert "needs_setup=1" in url
    assert "/auth/google" in url


def test_google_desktop_redirect_uses_desktop_scheme():
    url = frontend_redirect("desktop", "desk_tok", False)
    assert "token=desk_tok" in url
    assert "needs_setup=0" in url
    assert "chat.ssc.secure.desktop://" in url