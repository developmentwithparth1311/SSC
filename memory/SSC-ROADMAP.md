# SSC Roadmap — single source of truth

**Updated:** 2026-06-23  
**Repo:** `C:\Users\smash\SSC-main`  
**Rule:** After every engine step, feature, or deploy — update **this file only**. Do not maintain parallel roadmaps.

**Gate commands:** `backend/scripts/run_engineN_gate.py`  
**Security model:** `memory/SECURITY_MODEL.md`

---

## Live infrastructure (verified 23 Jun 2026)

| Service | URL / status | Notes |
|---------|----------------|-------|
| **Production API** | `https://ssc-api-4jp3wuccwa-ew.a.run.app` | Cloud Run · `env=production` · mongo ✅ · redis ✅ |
| **Firebase project** | `super-chat-b0992` | App Distribution, FCM push, Hosting (`super-chat-b0992.web.app`) |
| **MongoDB** | Atlas `ssc` cluster | Network: allow Cloud Run (0.0.0.0/0) |
| **Redis** | Upstash (production) | Required for `ENV=production` |
| **APK API URL** | Cloud Run (baked in build) | `frontend/.env.production.local` |
| **Google OAuth** | ✅ Configured | Web client + Cloud Run redirect URI in `cloud_run.env` |
| **LAN dev** | Optional | Founder laptop only — never give LAN IP to testers |

---

## Engine progress tree

```
Engines 1–5 + 8  ✅ COMPLETE (gates pass)
Engine 6         ⬜ PLANNED (push / own-metal)
Engine 7         — (not defined)
Engine 9         ⬜ PLANNED (on-device translation, close M5)
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

**Charter:** `memory/SIGNAL_PROTOCOL_CHARTER.md`

### Engine 6 — Push / own-metal ⬜
- [ ] Self-hosted push path evaluation
- [ ] Own-metal Mongo option (deferred post-investors)

### Engine 9 — Translation privacy ⬜
- [ ] On-device translation (close M5 plaintext egress)

---

## Signal coverage — whole app plan

**Your question:** Signal was added — shouldn't the **whole app** use it?

**Answer:** Yes, that is the **target**. Engine 8 v1 deliberately shipped **incrementally** so nothing broke. Current truth:

| Surface | Android APK | Web/PWA | Target phase |
|---------|-------------|---------|--------------|
| 1:1 text | ✅ `signal_v1` | Legacy RSA | 8.5 ✅ / Web → Engine 8+ |
| 1:1 call signaling | ✅ encrypted | Legacy cleartext | 8.7 ✅ / Web → 8+ |
| 1:1 attachments | Legacy RSA | Legacy RSA | **8+ / Engine 9** |
| Group messages | Legacy RSA | Legacy RSA | **Sender Keys (deferred)** |
| Group call signaling | Cleartext relay | Cleartext | **Sender Keys + SFU** |
| Stories / statuses | Legacy RSA | Legacy RSA | **8+** |
| Account unlock | RSA vault (PBKDF2) | Same | Keep (orthogonal to ratchet) |

**Next crypto phases (in order):**
1. [ ] Signal **attachments** (1:1, Android)
2. [ ] Signal on **Web** (libsignal WASM bridge)
3. [ ] **Group Sender Keys**
4. [ ] Unified identity (retire dual RSA + Curve25519 registration story)

Details: `memory/SECURITY_MODEL.md`

---

## Product features (MVP)

| Feature | Status |
|---------|--------|
| 1:1 + group chat | ✅ |
| E2E files (RSA envelope) | ✅ |
| Voice/video 1:1 + group (~6 mesh) | ✅ |
| Stories 24h | ✅ |
| Contacts + friend requests | ✅ |
| 2FA TOTP | ✅ |
| Panic wipe (keeps account + friends) | ✅ |
| Push FCM + Web VAPID | ✅ |
| PWA + Capacitor Android APK | ✅ |
| Google OAuth (web + native) | ✅ configured |
| Translation | ⚠️ Works but **breaks E2E** when enabled |
| iOS app | ⬜ Not started |
| Custom domain + Turnstile | ⬜ ~28 Jun 2026 |
| Play Store public | ⬜ AGPL review + listing |
| TURN self-host (off-LAN calls) | ⬜ Credentials exist; verify on phone |

---

## Open gaps (honest)

| ID | Item | Priority | Engine |
|----|------|----------|--------|
| M4 | Contacts graph server metadata | Accepted tradeoff | — |
| M5 | Translation plaintext when enabled | High | 9 |
| S3 | Native session lost on force-close | Medium | 5 doc |
| — | Group Sender Keys | High | 8+ |
| — | Signal on Web | High | 8+ |
| — | Signal attachments | Medium | 8+ |
| — | AGPL compliance before public Play | High | Legal |

**Closed:** G6, G9, C8

---

## Testing & deploy (founder — locked)

| Mode | Use |
|------|-----|
| LAN / localhost | Founder laptop only |
| **Firebase App Tester** | Real testers — production API URL in APK |
| **Cloud Run HTTPS** | `https://ssc-api-4jp3wuccwa-ew.a.run.app` |
| LAN IP | **Never** give to testers |

```powershell
cd C:\Users\smash\SSC-main\backend
.\venv\Scripts\python.exe scripts\run_engine8_gate.py
```

---

## Remaining work (priority order)

### P0 — Before wider testers
- [x] HTTPS production API (Cloud Run)
- [x] Google OAuth + Cloud Run redirect URI
- [x] APK bakes Cloud Run URL (`yarn cap:sync` / `SSC-BUILD-APK.bat`)
- [ ] Custom domain + Turnstile (~28 Jun)
- [ ] Sync PRD intro text (still says RSA-only — see `memory/PRD.md` header note)
- [ ] Two-phone smoke: Signal chat + call (founder manual)

### P1 — Product / security
- [ ] Engine 8+ phase 1: Signal attachments (1:1 Android)
- [ ] Engine 8+ phase 2: Signal on Web (WASM)
- [ ] Engine 9: on-device translation
- [ ] Group Sender Keys
- [ ] TURN verification on cellular/Wi‑Fi mix
- [ ] AGPL legal review

### P2 — Scale & polish
- [ ] Engine 6 own-metal / push hardening
- [ ] WebSocket Redis pub-sub (multi-worker)
- [ ] SFU for group calls >6
- [ ] iOS Capacitor ($99/yr)
- [ ] 2FA backup codes
- [ ] Invite links with handshake
- [ ] Frontend automated tests (0 today)
- [x] Remove dead shadcn `components/ui` scaffold

---

## Test health

| Metric | Value |
|--------|-------|
| pytest collected | **462** |
| Engine 8 gate | 50 unit + 10 integration + 37 proof |
| Frontend tests | 0 |

---

## Changelog

| Date | Milestone |
|------|-----------|
| 2026-06-17 | MVP iterations 1–3 |
| 2026-06-23 | Engines 1–5 complete |
| 2026-06-23 | Engine 8 complete (libsignal 0.96.2) |
| 2026-06-23 | Single roadmap file — retired duplicate Desktop roadmaps |
| 2026-06-23 | Cloud Run production API live; OAuth on Cloud Run redirect |