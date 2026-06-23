# SSC Session Hardening Charter

**Version:** 1.0  
**Effective:** 2026-06-23  
**Engine:** 5 — Session Hardening  
**Step:** 5.1 (policy only; enforcement in steps 5.2–5.7)

---

## 1. Purpose

Engines 1–4 minimized data, E2E honesty, client footprint, and metadata. Engine 5 closes **C8**: the JWT session token stored in `localStorage` — readable on a grabbed device and trivial to exfiltrate via XSS.

This charter defines:

- Where session tokens **may** live (web vs native)
- HttpOnly cookie path for browser/PWA
- In-memory-only path for Capacitor (App Tester APK)
- Logout, panic, and revocation alignment
- Production Redis revocation requirement
- Deployment/testing strategy (founder intent)

**Rule:** Engine 5 may proceed because Engine 4 gate passed (2026-06-23).

**Prerequisites:**
- Engine 1 complete (`memory/RETENTION_CHARTER.md`)
- Engine 2 complete (`memory/E2E_INTEGRITY_CHARTER.md`)
- Engine 3 complete (`memory/CLIENT_FOOTPRINT_CHARTER.md`)
- Engine 4 complete (`memory/METADATA_MINIMIZATION_CHARTER.md`)

---

## 2. Deployment & testing strategy (founder — locked)

| Mode | Who | How | HTTPS / domain |
|------|-----|-----|----------------|
| **LAN / localhost** | Founder only | PC browser `yarn start` → quick UI review | HTTP OK on laptop |
| **Real testers** | Invited users (e.g. wife) | **Firebase App Tester** — upload APK, add tester emails | APK built with **production API URL** (not LAN IP) |
| **Public website** | Everyone | Custom domain + HTTPS | **Deferred ~28 Jun 2026** — Turnstile + domain wait until then |

**Never expose** home LAN IP or `localhost` to testers. LAN is dev-preview only, not a distribution channel.

**App Tester flow:** testers receive invite → install via App Tester → log in → use SSC like any normal app against the deployed API.

---

## 3. Threat model

### 3.1 Grab-phone (inherits Engine 3)

Attacker has unlocked device with active SSC session.

| Storage | Risk today | Target (Engine 5) |
|---------|------------|-------------------|
| `localStorage.ssc_token` | JWT readable in DevTools / forensic dump | **Remove** — C8 |
| HttpOnly cookie (web) | Not readable from JS | **Use for browser** |
| React in-memory (native) | Gone on panic wipe; gone on force-close | **Use for Capacitor** |

### 3.2 XSS (web)

Any script injection could `localStorage.getItem('ssc_token')`. HttpOnly cookies are not accessible to `document.cookie` from JS when flags are correct.

### 3.3 Session replay

Logout and panic must revoke JWT in Redis (when available) and delete `user_sessions` row. Web must clear cookie; native must clear memory.

---

## 4. Session surfaces (code audit 2026-06-23)

### 4.1 Today

| Surface | Content | Problem |
|---------|---------|---------|
| `localStorage.ssc_token` | JWT | **C8** — persists across refresh; readable |
| `Authorization: Bearer` header | JWT from localStorage | Required today for API + native |
| `session_token` cookie | Supported in `get_current_user` | **Never set** on login/register |
| `user_sessions` MongoDB | session_token + expires_at | ✅ 7d TTL |
| Redis `ssc:revoked:*` | Logout revocation | Optional today; **required in prod** (step 5.6) |
| WS ticket | 60s one-time | ✅ — not long-lived JWT in URL |

### 4.2 Target

| Platform | Token storage | API auth |
|----------|---------------|----------|
| **Web / PWA** | HttpOnly `session_token` cookie (`Secure`, `SameSite=Lax`) | `withCredentials: true`; no JWT in JS |
| **Native (Capacitor)** | React state / session module only — **no localStorage** | `Authorization: Bearer` from memory |
| **Both** | WS via `POST /auth/ws-ticket` | Unchanged |

**Native tradeoff:** App restart requires re-login unless future secure enclave storage is added (out of Engine 5 scope).

---

## 5. Backend policy

### 5.1 Login / register response

| Field | Web target | Native target |
|-------|------------|---------------|
| JSON `token` | Omit or empty when cookie set | Return once for memory bootstrap |
| `Set-Cookie: session_token` | HttpOnly; `Secure` when HTTPS; `SameSite=Lax`; `Path=/`; max-age = JWT TTL | Not relied upon (Capacitor skips cookies) |

### 5.2 `get_current_user`

Priority unchanged: `Authorization` header **or** `session_token` cookie → JWT decode → `user_sessions` fallback.

### 5.3 Logout / panic

- Revoke JWT in Redis (TTL = remaining JWT life)
- Delete `user_sessions` document
- `delete_cookie("session_token")` on web responses

### 5.4 Production (`ENV=production`)

| Control | Rule |
|---------|------|
| `REDIS_URL` | **Required** — logout revocation must work |
| `JWT_SECRET` | 48+ random chars |
| Cookie `Secure` | **true** when request is HTTPS |

---

## 6. Client policy

### 6.1 Web

- Remove all `localStorage.setItem('ssc_token', …)` paths
- `api.js`: `withCredentials: true`; **no** Authorization interceptor reading localStorage
- `AuthContext`: session from `/auth/me` on load (cookie sent automatically)
- `loginWithToken`: web path sets user state only; cookie already set by server

### 6.2 Native (Capacitor / App Tester APK)

- Token held in `sessionStore` module (memory only)
- `api.js`: `withCredentials: false`; Authorization from memory
- Panic/logout: clear memory store (Engine 3 orchestrator)
- **Build-time** `REACT_APP_BACKEND_URL` = production HTTPS API — never LAN IP in tester builds

### 6.3 Footprint (closes C8)

| Key | Panic | Logout | Engine 5 step |
|-----|-------|--------|---------------|
| `ssc_token` | Must not exist after 5.3 | Must not exist after 5.3 | 5.3–5.5 |
| `ssc_native_push_token` | Remove (unchanged) | Remove | Engine 3 |

---

## 7. Gap summary

| ID | Gap | Severity | Engine 5 step |
|----|-----|----------|---------------|
| C8 | JWT in localStorage | **High** | 5.3–5.5 |
| S1 | Cookie never set on login | **High** | 5.2 |
| S2 | Redis revocation optional in dev | **Medium** | 5.6 ✅ |
| S3 | Native session lost on app kill | **Low** | Accepted — re-login |

**Deferred (not Engine 5):** custom domain (~28 Jun), Turnstile widget, Android Keystore persistence.

---

## 8. Engine 5 completion checklist

- [x] **5.1** Session Hardening Charter (this document + `backend/core/session_policy.py`)
- [x] **5.2** Backend HttpOnly session cookie on login/register/logout
- [x] **5.3** Web client cookie auth (remove localStorage JWT)
- [x] **5.4** Native in-memory session module (Capacitor path)
- [x] **5.5** Panic/logout/orchestrator + C8 footprint closure
- [x] **5.6** Production Redis revocation gate + session TTL alignment
- [x] **5.7** Engine 5 test gate

### Enforcement (Step 5.2)

| Control | Implementation |
|---------|----------------|
| `core/session_cookie.py` | `set_session_cookie`, `clear_session_cookie`, Secure/HttpOnly flags |
| `core/session_issue.py` | `create_session_token`, `issue_authenticated_session` |
| `routers/auth.py` | Cookie set on register/login/google; cleared on logout |

### Enforcement (Step 5.3)

| Control | Implementation |
|---------|----------------|
| `frontend/src/lib/sessionStore.js` | `usesCookieAuth`, `persistSessionToken` (web no-op), `purgeLegacyJwtFromStorage` |
| `frontend/src/lib/api.js` | `withCredentials: true` on web; no Bearer from localStorage |
| `frontend/src/context/AuthContext.jsx` | `loginWithToken` does not persist JWT on web |
| `core/google_auth.py` | Web OAuth redirect omits token from URL |

### Enforcement (Step 5.4)

| Control | Implementation |
|---------|----------------|
| `frontend/src/lib/sessionStore.js` | `nativeMemoryToken` only — no `localStorage` read/write for JWT |
| `frontend/src/lib/localStorageFootprint.js` | `ssc_token` in `LEGACY_JWT_PURGE_KEYS` only (never stored) |
| Native tradeoff | App force-close → re-login (S3 accepted) |

### Enforcement (Step 5.5)

| Control | Implementation |
|---------|----------------|
| `clientFootprintOrchestrator.js` | `clearSessionToken()` in phase 1; credentials captured before wipe |
| `routers/panic.py` | Cookie auth + `clear_session_cookie` on response |
| `routers/auth.py` | `resolve_request_session_token` for logout |
| `core/session_cookie.py` | Shared token resolution helper |
| Gap **C8** | Resolved — web cookie + native memory; legacy `ssc_token` purged |

### Enforcement (Step 5.6)

| Control | Implementation |
|---------|----------------|
| `core/session_ttl.py` | Canonical JWT / cookie / `user_sessions` TTL from `SESSION_JWT_TTL_DAYS` |
| `core/session_production.py` | `validate_production_redis` — fail fast when `ENV=production` |
| `security.py` | Startup calls production Redis gate (replaces warn-only) |
| `core/token_revocation.py` | Production logout/panic cannot silently skip revocation |
| `core/health_checks.py` | Production health errors when Redis missing/unreachable |
| `check_ready.py` | Production readiness includes Redis URL + ping |
| Gap **S2** | Resolved — Redis required in production; optional in dev |

### Enforcement (Step 5.7)

| Control | Implementation |
|---------|----------------|
| `scripts/run_engine5_gate.py` | Unit + integration + session proof |
| `scripts/session_proof.py` | Policy / enforcement audit |
| `core/session_proof.py` | Shared proof logic |
| `tests/test_engine5_gate.py` | Manifest sign-off |
| `tests/test_engine5_integration.py` | Live cookie auth + logout revocation |

**Run gate:**
```powershell
cd backend
.\venv\Scripts\python.exe scripts\run_engine5_gate.py
```

---

## 9. Sign-off (2026-06-23)

Engine 5 gate passed — step 5.7 complete:

- ✅ Web: no `ssc_token` in localStorage; HttpOnly cookie authenticates `/auth/me`
- ✅ Native: no `ssc_token` in localStorage; token in memory only
- ✅ Logout/panic revoke session server-side
- ✅ Production requires Redis for revocation
- ❌ No JWT in client-readable persistent storage

---

*Canonical copy: `SSC-main/memory/SESSION_HARDENING_CHARTER.md`*  
*Machine-readable: `SSC-main/backend/core/session_policy.py`*