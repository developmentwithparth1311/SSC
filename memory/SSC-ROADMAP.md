# SSC Roadmap — single source of truth

**Updated:** 2026-06-24 (installed-clients-only · Engine 10 desktop · group cap 8)
**Repo:** `C:\Users\smash\SSC-main`  
**Rule:** After every engine step, feature, or deploy — update **this file only**. Do not maintain parallel roadmaps.

**Gate commands:** `backend/scripts/run_engineN_gate.py`  
**Security model:** `memory/SECURITY_MODEL.md`

---

## Live infrastructure (verified 24 Jun 2026)

| Service | URL / status | Notes |
|---------|----------------|-------|
| **Production API** | `https://ssc-api-4jp3wuccwa-ew.a.run.app` | Cloud Run · `env=production` · mongo ✅ · redis ✅ |
| **Firebase project** | `super-chat-b0992` | App Distribution, FCM push, Hosting (`super-chat-b0992.web.app`) |
| **MongoDB** | Atlas `ssc` cluster | Network: allow Cloud Run (0.0.0.0/0) |
| **Redis** | Upstash (production) | Required for `ENV=production` |
| **APK API URL** | Cloud Run (baked in build) | `frontend/.env.production.local` |
| **Google OAuth** | ✅ Configured | Web client + Cloud Run redirect URI in `cloud_run.env` |
| **LAN dev** | ✅ Docker mongo + redis + local backend | Founder laptop only — never give LAN IP to testers |

---

## Engine progress tree

```
Engines 1–5 + 8 + 9  ✅ COMPLETE (gates pass)
Engine 6             ✅ EVALUATION (6.1–6.2 done · 6.3 deferred post-investors)
Engine 10            ✅ DESKTOP (Windows installer · Mac dmg config · libsignal)
```

### Engine 1 — Retention ✅
- [x] 1.1 Charter · 1.2 Plaintext leaks closed · 1.3 TTL indexes · 1.4 Conv metadata · 1.5 Logging · 1.6 Egress map · 1.7 Gate

### Engine 2 — E2E integrity ✅
- [x] 2.1–2.7 (vault, file ACL, API integrity, verification) · Gate ✅ · G1–G5, G7–G8 closed

### Engine 3 — Client footprint ✅
- [x] 3.1–3.7 (panic orchestrator, SW purge, localStorage policy) · Gate ✅

### Engine 4 — Metadata minimization ✅
- [x] 4.1–4.7 (last_seen, generic push, contacts tradeoff) · Gate ✅ · M1–M3, M6 closed

### Engine 5 — Session hardening ✅
- [x] 5.1–5.7 (HttpOnly cookie, native memory JWT, Redis revocation) · Gate ✅ · C8 closed

### Engine 8 — Signal Protocol ✅
- [x] 8.1 Charter + policy
- [x] 8.2 Safety numbers v3 + local QR
- [x] 8.3 Prekey API + libsignal **0.96.2** pinned
- [x] 8.4 X3DH session (1:1 Android)
- [x] 8.5 Double Ratchet `signal_v1` text (G9 closed)
- [x] 8.6 Dual-read RSA + SIG/RSA UI labels
- [x] 8.7 WebRTC 1:1 signaling encrypted (G6 closed)
- [x] 8.8 Full gate + live integration proof (50 unit + 10 integration + 37 proof checks)
- [x] 8.9 Signal **1:1 attachments** (Android — AES file + ratchet key envelope)
- [x] 8.11 **Group Sender Keys** `signal_group_v1` (Android — SKDM fan-out + type 7)
- [x] 8.13 Group **call signaling** encrypted via Sender Keys
- [x] 8.12 **Stories** `signal_status_v1` (Sender Keys + contact SKDM fan-out)
- [x] 8.10 Signal on **Web** — **retired** (no browser WASM; desktop libsignal = Engine 10)

**Charter:** `memory/SIGNAL_PROTOCOL_CHARTER.md`

### Engine 10 — Desktop clients ✅
- [x] 10.1 Desktop charter + policy (`memory/DESKTOP_CLIENT_CHARTER.md`)
- [x] 10.2 Electron + libsignal Node bridge (IPC parity with Android plugin)
- [x] 10.3 Windows installer (`SSC-BUILD-DESKTOP-WIN.bat` → NSIS `.exe`)
- [x] 10.4 Mac build config (`yarn desktop:build:mac` on macOS)
- [x] 10.5 Engine 10 gate + platform wiring

**Charter:** `memory/DESKTOP_CLIENT_CHARTER.md`

### Engine 6 — Push / own-metal ✅ (evaluation)
- [x] 6.1 Push path evaluation — keep FCM + VAPID; self-host deferred
- [x] 6.2 Own-metal Mongo evaluation — keep Atlas; deferred post-investors
- [ ] 6.3 Own-metal migration runbook (post-investors)

**Charter:** `memory/ENGINE_6_CHARTER.md`

### Engine 9 — Translation privacy ✅
- [x] 9.1 On-device translation policy + unified client
- [x] 9.2 ML Kit Capacitor plugin (Android `SscTranslate`)
- [x] 9.3 Message UI uses on-device translate (no server plaintext on APK)
- [x] 9.4 Engine 9 gate + M5 closed

---

## Signal coverage — whole app plan

**Your question:** Signal was added — shouldn't the **whole app** use it?

**Answer:** Yes, that is the **target**. Engine 8 v1 deliberately shipped **incrementally** so nothing broke. Current truth:

| Surface | Android | Windows/Mac desktop | Browser (dev only) |
|---------|---------|---------------------|-------------------|
| 1:1 text | ✅ `signal_v1` | ✅ `signal_v1` | Legacy RSA (not product) |
| 1:1 call signaling | ✅ encrypted | ✅ encrypted | Legacy |
| 1:1 attachments | ✅ `signal_v1` | ✅ `signal_v1` | Legacy RSA |
| Group messages | ✅ `signal_group_v1` | ✅ `signal_group_v1` | Legacy RSA |
| Group call signaling | ✅ encrypted | ✅ encrypted | Legacy |
| Stories / statuses | ✅ `signal_status_v1` | ✅ `signal_status_v1` | Legacy RSA |
| Account unlock | RSA vault (PBKDF2) | Same | Same |

**Product surfaces:** Android APK · Windows `.exe` · Mac `.dmg` (build on Mac) · iOS deferred.

**Next crypto / identity (P1):**
1. [ ] **Unified identity** — libsignal curve primary; reset 3 tester accounts OK
2. [ ] **Contacts graph privacy** — server must not see who is friends with whom

Details: `memory/SECURITY_MODEL.md`

---

## Product features (MVP)

| Feature | Status |
|---------|--------|
| 1:1 + group chat | ✅ |
| E2E files (RSA envelope) | ✅ |
| Voice/video 1:1 + group (mesh up to **8**) | ✅ |
| Stories 24h | ✅ |
| Contacts + friend requests | ✅ |
| 2FA TOTP + backup codes | ✅ |
| Panic wipe (keeps account + friends) | ✅ |
| Push FCM + Web VAPID | ✅ |
| Capacitor Android APK | ✅ |
| Windows desktop (Electron + libsignal) | ✅ |
| Mac desktop (`.dmg` on macOS) | ✅ config · build on Mac |
| Web / PWA in browser | ⬜ **Not a product** — dev/landing only (RSA) |
| Google OAuth (web + native) | ✅ configured |
| Translation | ✅ On-device (Android ML Kit); server off by default |
| iOS app | ⬜ Deferred · scaffold exists (`frontend/ios/`) |
| Custom domain + Turnstile | ⬜ ~28 Jun 2026 |
| Play Store public | ⬜ Listing (AGPL review ✅) |
| TURN self-host (off-LAN calls) | ⬜ Credentials exist; verify on phone |

---

## Open gaps (honest)

| ID | Item | Priority | Engine |
|----|------|----------|--------|
| M4 | Contacts graph server metadata | **High — fix** (staff-blind graph) | 11+ |
| S3 | Native session lost on force-close | Low (accepted) | 5 doc |
| — | Unified identity (RSA + Curve25519) | **High** | P1 |
| — | iOS libsignal + App Store | Deferred | — |


**Closed:** G6, G9, C8, M5

---

## Testing & deploy (founder — locked)

| Mode | Use |
|------|-----|
| LAN / localhost | Founder laptop only |
| **Firebase App Distribution** | Real testers — production API URL in APK |
| **Cloud Run HTTPS** | `https://ssc-api-4jp3wuccwa-ew.a.run.app` |
| LAN IP | **Never** give to testers |

```powershell
cd C:\Users\smash\SSC-main\backend
.\venv\Scripts\python.exe scripts\run_engine8_gate.py
.\venv\Scripts\python.exe scripts\run_engine9_gate.py
```

---

## Remaining work (priority order)

### P0 — Before wider testers
- [x] HTTPS production API (Cloud Run)
- [x] Google OAuth + Cloud Run redirect URI
- [x] APK bakes Cloud Run URL (`yarn cap:sync` / `SSC-BUILD-APK.bat`)
- [ ] Custom domain + Turnstile (~28 Jun)
- [x] Sync PRD intro text (`memory/PRD.md` updated 24 Jun 2026)
- [x] Automated smoke: `e2e_smoke.py` + Engine 1–5/8/9 gates + production `/api/health` (24 Jun 2026)
- [ ] Two-phone smoke: Signal chat + call + on-device translate (founder manual — APK on device)
- [ ] TURN verification on cellular/Wi‑Fi mix (founder manual — same session as two-phone)

### P1 — Product / security
- [x] Engine 8.9: Signal attachments (1:1 Android)
- [x] Engine 8.11: Group Sender Keys
- [x] Engine 8.12: Stories Signal encryption
- [x] Engine 8.13: Group call signaling encryption
- [x] Engine 8.10: Signal on Web — **retired** (Engine 10 desktop instead)
- [x] Engine 9: on-device translation (M5)
- [x] Engine 10: Windows + Mac desktop (`memory/DESKTOP_CLIENT_CHARTER.md`)
- [ ] Unified identity (libsignal curve primary · 3 testers)
- [ ] Contacts graph privacy (server-blind friend graph)
- [x] AGPL legal review (`memory/AGPL_COMPLIANCE.md`, `LICENSE`, in-app source offer)
- [x] Group video cap **8** (mesh; SFU for 9+ deferred to domain ~28 Jun)

### P2 — Scale & polish
- [x] Engine 6 evaluation (push + own-metal — charter + gate; migration deferred)
- [x] WebSocket Redis pub-sub (multi-worker — Redis fan-out + global online set)
- [x] SFU Phase A — charter + `/api/config` + mesh cap enforcement (mediasoup deploy = Phase B)
- [x] iOS Capacitor scaffold (`cap add ios` + charter; App Store build deferred — needs Mac)
- [x] 2FA backup codes (10 codes on setup, login fallback, regenerate in UI)
- [x] Invite links — **retired** (username search + friend requests sufficient)
- [x] Frontend automated tests (`yarn test:ci` — 13 tests, 4 suites)
- [x] Remove dead shadcn `components/ui` scaffold

---

## Test health (verified 24 Jun 2026)

| Metric | Value |
|--------|-------|
| pytest collected | **477** |
| pytest result | **476 passed**, 1 skipped, 0 failed |
| Engine 1–5 gates | **PASS** |
| Engine 8 gate | **PASS** (54 unit + 10 integration + proof through 8.12) |
| Engine 9 gate | **PASS** |
| `e2e_smoke.py` | **PASS** (health, contacts, messages, files, statuses, panic wipe) |
| Production `/api/health` | **PASS** (`env=production`, mongo + redis ok) |
| WS fan-out | Redis pub-sub when `REDIS_URL` set · `ws_fanout` in `/api/health` |
| Frontend tests | **22 passed** (`yarn test:ci` — platform + groupCalls cap 8) |
| AGPL gate | **PASS** (`run_agpl_gate.py`) |
| Engine 10 gate | **PASS** (`run_engine10_gate.py`) |

---

## Changelog

| Date | Milestone |
|------|-----------|
| 2026-06-17 | MVP iterations 1–3 |
| 2026-06-23 | Engines 1–5 complete |
| 2026-06-23 | Engine 8 complete (libsignal 0.96.2) |
| 2026-06-23 | Engine 8.9 — Signal 1:1 attachments (Android) |
| 2026-06-23 | Engine 8.11 — Group Sender Keys `signal_group_v1` |
| 2026-06-23 | Engine 8.12 — Stories `signal_status_v1` |
| 2026-06-23 | Engine 8.13 — Group call signaling encrypted |
| 2026-06-23 | Single roadmap file — retired duplicate Desktop roadmaps |
| 2026-06-23 | Cloud Run production API live; OAuth on Cloud Run redirect |
| 2026-06-23 | Engine 9 — on-device translation (ML Kit Android); M5 closed |
| 2026-06-23 | `yarn cap:sync` rebuild — Engine 9 + Signal 8.9–8.13 baked into APK |
| 2026-06-24 | Test drift fixed (3 policy assertions for 8.9–8.12 + Firebase App Distribution) |
| 2026-06-24 | `e2e_smoke.py` panic-wipe check aligned with session revocation; smoke green |
| 2026-06-24 | All Engine 1–5/8/9 gates pass; pytest 476/476 (1 skipped) |
| 2026-06-24 | Roadmap cleanup: Engine 7 removed, 2FA backups marked done, invite links retired |
| 2026-06-24 | Invite links removed from codebase (username search + friend requests only) |
| 2026-06-24 | PRD synced to current architecture (Signal Android, Engine 9, production deploy) |
| 2026-06-24 | Frontend automated tests — 13 tests (i18n, presence, session footprint, Landing) |
| 2026-06-24 | Engine 6 evaluation — push/own-metal charter + policy gate (6.1–6.2) |
| 2026-06-24 | WebSocket Redis pub-sub — multi-worker fan-out + push offline fix |
| 2026-06-24 | SFU Phase A — mediasoup selected; config + mesh cap; deploy deferred |
| 2026-06-24 | iOS Capacitor scaffold — `frontend/ios/` + IOS_CAPACITOR_CHARTER.md |
| 2026-06-24 | AGPL legal review — LICENSE, THIRD_PARTY_NOTICES, compliance doc, in-app source offer, gate |
| 2026-06-24 | Installed-clients-only product strategy — Web/PWA retired as product surface |
| 2026-06-24 | Engine 10 — Electron desktop + libsignal (Windows NSIS · Mac dmg config) |
| 2026-06-24 | Group video mesh cap raised to **8**; contacts privacy + unified identity locked P1 |