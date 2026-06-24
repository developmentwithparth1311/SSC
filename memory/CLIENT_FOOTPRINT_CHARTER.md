# SSC Client Footprint Charter

**Version:** 1.0  
**Effective:** 2026-06-23  
**Engine:** 3 — Client Footprint / Grab-Phone Hardening  
**Step:** 3.1 (policy only; enforcement in steps 3.2–3.7)

---

## 1. Purpose

Engine 1 ensured **minimum data on the server**. Engine 2 ensured **cryptographic honesty** (E2E paths are real). Engine 3 ensures **minimum readable footprint on the device** — especially under the **grab-phone** threat: someone takes an unlocked phone and tries to read chats before the user recovers it.

This charter defines:

- Every **client storage surface** (localStorage, sessionStorage, memory, SW cache, IndexedDB)
- What must be **wiped on panic** vs **logout** vs **kept** (preferences)
- How client wipe **coordinates** with server `POST /api/panic-wipe`
- Gaps between **today's code** and **target**
- Enforcement steps 3.2–3.7

**Rule:** Engine 3 complete (3.7 gate passed 2026-06-23). Engine 4 complete (4.7 gate passed 2026-06-23) — see `METADATA_MINIMIZATION_CHARTER.md`.

**Prerequisites:**
- Engine 1 complete (`memory/RETENTION_CHARTER.md` + gate passed)
- Engine 2 complete (`memory/E2E_INTEGRITY_CHARTER.md` + gate passed)

---

## 2. Vision alignment

| Principle | Meaning for client footprint |
|-----------|------------------------------|
| Panic = grab phone | Wipe **readable** data on device **immediately**; server purge follows |
| Account survives | Login still works after panic — server keeps `users` row (Engine 1) |
| Super secure | Minimize what a forensic read of the device finds after panic |
| E2E honest | Engine 2 already keeps decrypted keys out of storage; Engine 3 clears **plaintext in memory** |

---

## 3. Threat model

### 3.1 Grab-phone (primary)

Attacker has **physical access** to an **unlocked** SSC session (vault may or may not be unlocked).

**Goal:** No decrypted message bodies, attachment previews, or session tokens remain readable **after panic completes**.

**Not in scope for Engine 3:** Attacker with **root/kernel** access or **cold boot** RAM forensics (inherent limit).

### 3.2 Normal logout

User chooses to sign out. Same memory wipe as panic for secrets; **may** retain non-sensitive preferences (`ssc_ui_lang`).

### 3.3 Refresh / tab close / force-stop

Private key: memory only; TASK A auto-unlocks from device wrap. **JWT (TASK B):** `ssc_session_wrap_enc` survives force-close; cleared on logout/panic. Never plaintext `ssc_token`.

---

## 4. Panic flow (target)

```
User holds PANIC 1.5s
  → 1. Client instant wipe (Engine 3) — memory, blobs, storage secrets
  → 2. POST /api/panic-wipe (server) — conversations, files, statuses
  → 3. Redirect /login?panic=1
```

**Enforced (3.6):** Step 1 is **synchronous and complete** before step 2 starts (`clientFootprintOrchestrator.js`).

---

## 5. Client storage inventory (code audit 2026-06-23)

### 5.1 localStorage

| Key / pattern | Tier | Panic | Logout | Step |
|---------------|------|-------|--------|------|
| `ssc_token` | Secret | Remove ✅ | Remove ✅ | — (legacy; never written) |
| `ssc_session_wrap_enc` | Secret | Remove ✅ | Remove ✅ | TASK B |
| `ssc_device_wrap_secret` | Secret | Keep | Keep | device AES key |
| `ssc_vault_wrap_*` | Secret | Remove ✅ | Remove ✅ | TASK A |
| `ssc_native_push_token` | Session | Remove ✅ | Remove ✅ | — |
| `ssc_verified_v2_*` | Session | Remove ✅ | Keep | ✅ 3.4 |
| `ssc_ui_lang` | Preference | Keep | Keep | — |
| ~~`ssc_verified_*` (legacy)~~ | — | Purge on startup ✅ | — | Engine 2.6 |

### 5.2 sessionStorage

| Key | Tier | Panic | Logout | Step |
|-----|------|-------|--------|------|
| `ssc_pending_call` | Session | Clear ✅ (`clear()`) | Clear | — |
| `ssc_pending_invite` | Session | Clear ✅ | Clear | — |
| ~~`ssc_pk_jwk` / `ssc_pk_unlocked`~~ | Secret | Purge startup ✅ | — | Engine 2.2 |

### 5.3 React / in-memory (EPHEMERAL)

| State | Content | Panic target | Step |
|-------|---------|--------------|------|
| `AuthContext.privateKey` | Decrypted RSA key | Null ✅ | — |
| `ChatHome.messages` | Ciphertext + metadata | Wipe before redirect | ✅ 3.2 |
| `ChatHome.decryptedBodies` | Decrypted search cache | Wipe before redirect | ✅ 3.2 |
| `Message` component state | Decrypted plaintext per bubble | Wipe before redirect | ✅ 3.2 |
| Blob URLs (`Message.jsx`) | Decrypted attachment bytes | `revokeObjectURL` all | ✅ 3.2 |
| `ChatSocket` | WS connection + frames | Close + drop | ✅ 3.2 |

### 5.4 Service worker

| Asset | Content | Panic target | Step |
|-------|---------|--------------|------|
| `public/sw.js` | Push handler, no message body | — | — |
| Cache `ssc-v1` | PWA shell (if populated) | Delete all caches | ✅ 3.3 |

### 5.5 IndexedDB

| Usage today | Panic target | Step |
|-------------|--------------|------|
| No SSC-owned DBs in app code (audit 2026-06-23) | Delete all via `indexedDB.databases()` | ✅ 3.5 |

---

## 6. Server coordination

`POST /api/panic-wipe` (`core/panic_wipe_service.py`) deletes:

- All conversations the user is in — **sent and received** messages, read state
- Files the user uploaded **and** attachment files in those chats (including received media)
- User's stories/statuses and call records (if any)
- Sessions and push endpoints (forces re-login)

**Does not delete:** `users` (account), contact graph (`contact_seals` / `contact_rosters`), `friend_requests` — login and friend list survive (wife scenario).

Client panic **must not** depend on server success to wipe local secrets (offline-safe wipe in 3.6).

---

## 7. Gap summary

| ID | Gap | Severity | Engine 3 step |
|----|-----|----------|---------------|
| C1 | Decrypted text in React state until redirect | **Critical** | 3.2 ✅ |
| C2 | Blob URLs not centrally revoked | **High** | 3.2 ✅ |
| C3 | No unified wipe orchestrator | **High** | 3.6 ✅ |
| C4 | Service worker caches not purged | **Medium** | 3.3 ✅ |
| C5 | `ssc_verified_v2_*` survives panic | **Medium** | 3.4 ✅ |
| C6 | IndexedDB not audited | **Medium** | 3.5 ✅ |
| C7 | Client wipe after async server call | **Medium** | 3.6 ✅ |
| C8 | JWT in localStorage | **High** | Engine 5 |

---

## 8. Engine 3 completion checklist

- [x] **3.1** Client Footprint Charter (this document + `backend/core/client_footprint_policy.py`)
- [x] **3.2** Instant in-memory wipe on panic/logout

### Enforcement (Step 3.2)

| Control | Implementation |
|---------|----------------|
| `frontend/src/lib/memoryWipe.js` | `dispatchMemoryWipe`, blob registry, socket closers |
| `frontend/src/context/AuthContext.jsx` | Wipe before logout/panic server calls |
| `frontend/src/pages/ChatHome.jsx` | Clears messages, decryptedBodies, closes socket |
| `frontend/src/components/Message.jsx` | Wipe plaintext state; tracked blob URLs |
| `frontend/src/components/Stories.jsx` | StoryViewer clears decoded text on wipe |
- [x] **3.3** Service worker cache purge

### Enforcement (Step 3.3)

| Control | Implementation |
|---------|----------------|
| `frontend/src/lib/serviceWorkerCache.js` | `purgeServiceWorkerCaches()` — page + SW |
| `frontend/public/sw.js` | `SSC_PURGE_CACHES` message handler |
| `frontend/src/lib/memoryWipe.js` | Invokes cache purge on every wipe |
- [x] **3.4** localStorage panic policy (`ssc_verified_v2_*` clear on panic)

### Enforcement (Step 3.4)

| Control | Implementation |
|---------|----------------|
| `frontend/src/lib/verification.js` | `purgeVerificationStorageOnPanic()` — all `ssc_verified_v2_*` + legacy |
| `frontend/src/lib/localStorageFootprint.js` | `applyLocalStoragePanicPolicy()` — panic-only gate |
| `frontend/src/lib/memoryWipe.js` | Invokes localStorage panic policy when `reason === 'panic'` |
- [x] **3.5** IndexedDB audit and purge

### Enforcement (Step 3.5)

| Control | Implementation |
|---------|----------------|
| `backend/core/indexeddb_audit.py` | Source audit manifest — no SSC IndexedDB usage |
| `frontend/src/lib/indexedDBFootprint.js` | `purgeIndexedDBFootprint()` — delete all origin DBs |
| `frontend/src/lib/memoryWipe.js` | Invokes IndexedDB purge on every wipe |
- [x] **3.6** Unified panic wipe orchestrator (client-first)

### Enforcement (Step 3.6)

| Control | Implementation |
|---------|----------------|
| `frontend/src/lib/clientFootprintOrchestrator.js` | `executeClientFootprintWipe`, `runPanicOrchestrator`, `runLogoutOrchestrator` |
| `frontend/src/lib/localStorageFootprint.js` | `clearLocalStorageSessionSecrets()` |
| `frontend/src/lib/sessionStorageFootprint.js` | `clearSessionStorageFootprint()` |
| `frontend/src/context/AuthContext.jsx` | Delegates to orchestrator; auth state via `registerMemoryWipeHandler` |
- [x] **3.7** Engine 3 test gate

### Enforcement (Step 3.7)

| Control | Implementation |
|---------|----------------|
| `scripts/run_engine3_gate.py` | Unit tests + integration + footprint proof orchestrator |
| `scripts/client_footprint_proof.py` | Policy, gaps, enforcement artifact verification |
| `backend/core/client_footprint_proof.py` | Machine-readable proof manifest |
| `tests/test_engine3_gate.py` | Gate sign-off unit checks |
| `tests/test_engine3_integration.py` | Live panic wipe: chats gone, account + contacts remain |

```powershell
cd backend
.\venv\Scripts\python.exe scripts\run_engine3_gate.py
```

---

## 9. Sign-off (Engine 3 complete)

After panic on an unlocked device, a forensic reader of the browser profile should find:

- ❌ No decrypted message text in memory (post-redirect)
- ❌ No `ssc_token` or push tokens in localStorage
- ❌ No `ssc_verified_v2_*` entries (panic only)
- ❌ No attachment blob URLs
- ✅ `ssc_ui_lang` may remain (preference)
- ✅ Account still loginable (server `users` row intact)

---

*Canonical copy: `SSC-main/memory/CLIENT_FOOTPRINT_CHARTER.md`*  
*Machine-readable: `SSC-main/backend/core/client_footprint_policy.py`*  
*Depends on: `RETENTION_CHARTER.md` (Engine 1), `E2E_INTEGRITY_CHARTER.md` (Engine 2)*