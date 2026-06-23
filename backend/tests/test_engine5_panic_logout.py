"""Engine 5 Step 5.5 — panic/logout orchestrator + C8 closure."""
from pathlib import Path

from core.client_footprint_policy import FOOTPRINT_GAPS, CLIENT_WIPE_PHASE_1
from core.client_footprint_proof import run_client_footprint_proof
from core.session_cookie import resolve_request_session_token
from core.session_policy import ENGINE5_STEPS, SESSION_GAPS

REPO = Path(__file__).resolve().parents[2]
FRONTEND = REPO / "frontend" / "src"


def test_engine5_step_5_5_marked_complete():
    done = {step_id: complete for step_id, _, complete in ENGINE5_STEPS}
    assert done["5.5"] is True


def test_c8_footprint_gap_resolved():
    c8 = next(g for g in FOOTPRINT_GAPS if g.gap_id == "C8")
    assert c8.resolved is True


def test_c8_session_gap_resolved():
    c8 = next(g for g in SESSION_GAPS if g.gap_id == "C8")
    assert c8.resolved is True


def test_client_footprint_proof_c8_no_longer_deferred():
    report = run_client_footprint_proof()
    gap_check = next(c for c in report.checks if c.name == "engine3_gaps_resolved")
    assert gap_check.passed, gap_check.detail


def test_phase1_includes_clear_session_token():
    assert "clearSessionToken" in CLIENT_WIPE_PHASE_1
    orch = (FRONTEND / "lib" / "clientFootprintOrchestrator.js").read_text(encoding="utf-8")
    assert "clearSessionToken()" in orch
    idx_wipe = orch.index("executeClientFootprintWipe")
    body = orch[idx_wipe:]
    assert body.index("dispatchMemoryWipe") < body.index("clearSessionToken()")
    assert body.index("clearSessionToken()") < body.index("clearLocalStorageSessionSecrets")


def test_panic_route_clears_cookie_and_reads_cookie():
    panic = (REPO / "backend" / "routers" / "panic.py").read_text(encoding="utf-8")
    assert "Cookie(None)" in panic
    assert "clear_session_cookie" in panic
    assert "resolve_request_session_token" in panic


def test_logout_uses_resolve_request_session_token():
    auth = (REPO / "backend" / "routers" / "auth.py").read_text(encoding="utf-8")
    assert "resolve_request_session_token" in auth


def test_resolve_request_session_token_prefers_bearer():
    assert resolve_request_session_token("Bearer abc", "cookie_tok") == "abc"


def test_resolve_request_session_token_falls_back_to_cookie():
    assert resolve_request_session_token(None, "cookie_tok") == "cookie_tok"


def test_orchestrator_capture_before_wipe_for_native_bearer():
    orch = (FRONTEND / "lib" / "clientFootprintOrchestrator.js").read_text(encoding="utf-8")
    panic_start = orch.index("export async function runPanicOrchestrator")
    panic_body = orch[panic_start:]
    assert panic_body.index("capturePreWipeCredentials") < panic_body.index("executeClientFootprintWipe")
    logout_start = orch.index("export async function runLogoutOrchestrator")
    logout_body = orch[logout_start:]
    assert logout_body.index("capturePreWipeCredentials") < logout_body.index("executeClientFootprintWipe")