"""Engine 5 Step 5.4 — native in-memory session (source enforcement)."""
from pathlib import Path

from core.session_policy import ENGINE5_STEPS

REPO = Path(__file__).resolve().parents[2]
FRONTEND = REPO / "frontend" / "src"


def test_engine5_step_5_4_marked_complete():
    done = {step_id: complete for step_id, _, complete in ENGINE5_STEPS}
    assert done["5.4"] is True


def test_session_store_native_memory_only():
    text = (FRONTEND / "lib" / "sessionStore.js").read_text(encoding="utf-8")
    assert "nativeMemoryToken" in text
    assert "localStorage.setItem" not in text
    assert "localStorage.getItem" not in text
    assert "hasNativeSessionToken" in text
    assert "purgeLegacyJwtFromStorage" in text


def test_local_storage_footprint_jwt_purge_only():
    text = (FRONTEND / "lib" / "localStorageFootprint.js").read_text(encoding="utf-8")
    assert "LEGACY_JWT_PURGE_KEYS" in text
    assert "SESSION_SECRET_KEYS = ['ssc_native_push_token']" in text
    assert "LEGACY_JWT_KEY" not in text.split("SESSION_SECRET_KEYS")[1].split("]")[0]


def test_api_js_bearer_from_session_store_not_localstorage():
    text = (FRONTEND / "lib" / "api.js").read_text(encoding="utf-8")
    assert "getSessionToken()" in text
    assert "localStorage" not in text


def test_native_push_uses_session_store():
    text = (FRONTEND / "lib" / "native-push.js").read_text(encoding="utf-8")
    assert "getSessionToken" in text
    assert "localStorage.getItem('ssc_token')" not in text


def test_orchestrator_native_uses_session_store():
    text = (FRONTEND / "lib" / "clientFootprintOrchestrator.js").read_text(encoding="utf-8")
    assert "getSessionToken()" in text
    assert "localStorage.getItem('ssc_token')" not in text