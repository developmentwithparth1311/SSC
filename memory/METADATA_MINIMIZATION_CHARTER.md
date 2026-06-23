# SSC Metadata Minimization Charter

**Version:** 1.0  
**Effective:** 2026-06-23  
**Engine:** 4 — Metadata Minimization  
**Step:** 4.1 (policy only; enforcement in steps 4.2–4.7)

---

## 1. Purpose

Engines 1–3 minimized **data existence**, **cryptographic honesty**, and **client footprint**. Engine 4 minimizes **metadata** the server and third parties can learn about users — without breaking core app function.

This charter defines:

- What metadata SSC **may** store and expose
- How `last_seen` is **throttled, TTL'd, and coarsened**
- Push notification **generic-only** rule
- Accepted **contacts graph** tradeoff
- Gaps deferred to later engines (translation, Signal Protocol, WebRTC)

**Rule:** Engine 4 may proceed because Engine 3 gate passed (2026-06-23).

**Prerequisites:**
- Engine 1 complete (`memory/RETENTION_CHARTER.md`)
- Engine 2 complete (`memory/E2E_INTEGRITY_CHARTER.md`)
- Engine 3 complete (`memory/CLIENT_FOOTPRINT_CHARTER.md`)

---

## 2. Vision alignment

| Principle | Meaning for metadata |
|-----------|---------------------|
| Super secure | Reduce stalking surface — coarse presence, generic push |
| Account survives | `users` row persists; `last_seen` may expire but account remains |
| Own metal | Push still egresses via FCM/Web Push when enabled — minimize visible payload |
| Global users | Built-in translation (future) must not leak plaintext — Engine 9 |

---

## 3. last_seen policy (Steps 4.2–4.3)

### 3.1 Storage

| Control | Value | Implementation |
|---------|-------|----------------|
| Write throttle | 5 minutes | `touch_last_seen()` — skip DB write if recent |
| Storage TTL | 7 days | Expired values treated as unknown; not exposed to peers |
| Peer coarsening | 15m / 1h / 1d buckets | `coarsen_last_seen()` on API read |
| Online window | 5 minutes | Peers see `online: true` — **no exact timestamp** |

### 3.2 API projection

Peers receive:

```json
{ "online": true, "last_seen": null }
```

or

```json
{ "online": false, "last_seen": "2026-06-23T14:00:00+00:00" }
```

(coarsened bucket start — never sub-minute precision)

**Self** (`GET /auth/me`): full internal `last_seen` unchanged for own session diagnostics.

### 3.3 Enforcement

| Control | Implementation |
|---------|----------------|
| `core/last_seen.py` | Throttle, TTL, coarsen, `project_user_for_peer` |
| `routers/messages.py` | `touch_last_seen` on send |
| `routers/ws_handler.py` | `touch_last_seen` on WS connect |
| `core/conversation_meta.py` | `peer_summary` uses presence projection |
| `routers/contacts.py` | Contact list uses `project_user_for_peer` |

---

## 4. Push payload policy (Steps 4.4–4.5)

### 4.1 Visible notification (OS tray)

| Field | Allowed | Forbidden |
|-------|---------|-----------|
| `title` | `"SSC"` | `@username`, group names |
| `body` | `"New activity"` | Message text, "Sent a photo", "Incoming call from @x" |

### 4.2 Data payload (routing — third-party egress)

| Allowed | Forbidden |
|---------|-----------|
| `type` (message, call, friend_request, …) | `author_username`, `group_name` |
| `conversation_id` (opaque) | Message type hints in body |
| `from` (opaque user_id) | Decrypted content |
| `mode` (audio/video for calls) | |

**Tradeoff:** FCM/Web Push still see device tokens and opaque routing ids — documented as accepted for mobile reach.

### 4.3 Enforcement

| Control | Implementation |
|---------|----------------|
| `core/push_payload.py` | `build_generic_push`, `sanitize_push_data` |
| `push.py` | All `send_push_for_*` use generic builder |
| `native_push.py` | `_flatten_data` uses sanitizer |
| `frontend/public/sw.js` | Generic defaults; call actions preserved |

---

## 5. Contacts metadata (Step 4.6)

### Decision (v1.0 — accepted tradeoff)

The `contacts` collection **remains persistent** because:

1. Friend list is required for messaging and panic UX (wife scenario — account + friends survive panic)
2. Only stores `user_id`, `contact_id`, `blocked`, `muted`, `created_at` — no message content
3. Alternative (re-derive graph from ciphertext only) is Engine 8+ scope

| Gap ID | Status |
|--------|--------|
| M4 | **Accepted tradeoff** — documented, not a blocker |

---

## 6. Deferred gaps (not Engine 4)

| ID | Gap | Engine |
|----|-----|--------|
| M5 | Translation plaintext egress when enabled | 9 |
| M6 | WebRTC signaling cleartext | 8 |
| G9 | Signal Protocol / libsignal Double Ratchet | 8 |

**Translation note:** Current server-side translate stays available for dev/demo (`TRANSLATION_ENABLED=false` default). Future on-device translation preferred.

---

## 7. Engine 4 completion checklist

- [x] **4.1** Metadata Minimization Charter (this document + `backend/core/metadata_policy.py`)
- [x] **4.2** last_seen write throttling + 7-day TTL
- [x] **4.3** last_seen coarsening + `online` flag on peer API
- [x] **4.4** Generic push title/body
- [x] **4.5** Push data payload sanitization
- [x] **4.6** Contacts metadata tradeoff documented
- [x] **4.7** Engine 4 test gate

### Enforcement (Step 4.7)

| Control | Implementation |
|---------|----------------|
| `scripts/run_engine4_gate.py` | Unit tests + integration + metadata proof |
| `scripts/metadata_proof.py` | Policy / enforcement file audit |
| `core/metadata_proof.py` | Shared proof logic for scripts and tests |
| `tests/test_engine4_integration.py` | Live-server metadata guarantees |
| `tests/test_engine4_gate.py` | Manifest + sign-off checklist |

**Run gate:**
```powershell
cd backend
.\venv\Scripts\python.exe scripts\run_engine4_gate.py
```

---

## 8. Sign-off

After step 4.7, an operator should verify:

- ✅ Peer API responses expose `online` boolean and coarsened `last_seen` only
- ✅ Push payloads use generic title/body everywhere
- ✅ Contacts graph persists with documented tradeoff
- ❌ No usernames in push notification bodies

---

*Canonical copy: `SSC-main/memory/METADATA_MINIMIZATION_CHARTER.md`*  
*Machine-readable: `SSC-main/backend/core/metadata_policy.py`*