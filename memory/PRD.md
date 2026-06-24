# SSC — Super Secure Chat · PRD

> **Roadmap (single source of truth):** `memory/SSC-ROADMAP.md`  
> **Security model:** `memory/SECURITY_MODEL.md`  
> **Updated:** 2026-06-24

## Product summary

SSC is a hybrid full-stack E2E-encrypted ephemeral messaging app (WhatsApp/Telegram-style). Chats, files, calls, and stories auto-delete after 24h. Contacts are added via **username search + mutual friend requests** (invite links retired).

**Platforms (product):** **Installed clients only** — Android APK · Windows desktop · Mac desktop.  
**Not a product:** browser-tab Web/PWA (RSA legacy — founder dev / landing only).  
**Deferred:** iOS App Store (scaffold exists).  
Production API on Cloud Run HTTPS.

## Original problem statement

Build a WhatsApp/Telegram-like app with:

- 24h auto-recycle of chats, calls, files
- Built-in auto-translation
- Strong E2E encryption (libsignal on installed clients)
- Voice, video calls, file send/receive
- Panic wipe/log-out (keeps account + friends)
- Login: email+password OR Google (no phone number)
- Recovery via email+password only
- Username creation rules (4–12, no abuse, no SSC, no admin, no emoji)
- Anti-phishing, anti-bot, anti-spam
- Works on **installed** Android + Windows + Mac apps

## Architecture (current)

- **Backend:** FastAPI + MongoDB Atlas (TTL indexes for 24h auto-delete) + Redis (production rate limits + session revocation)
- **Production API:** `https://ssc-api-4jp3wuccwa-ew.a.run.app` (Cloud Run)
- **Realtime:** WebSocket (`/api/ws`) for messages, typing, read receipts, WebRTC signaling
- **E2E encryption (installed clients):**
  - **Android + Windows + Mac:** Signal Protocol (libsignal **0.96.2**) on 1:1, groups, stories, attachments, call signaling
  - **Browser dev shell:** Legacy RSA only — not marketed to users
  - **Account unlock:** RSA vault wrapped with PBKDF2(password) — orthogonal to ratchet
  - Server only stores ciphertext
- **Auth:** HttpOnly cookie (browser dev) + in-memory JWT (installed clients) · email/password · Google OAuth · TOTP 2FA · backup codes · Turnstile (production) · rate limiting
- **Translation:** On-device ML Kit on Android; server translation **off by default**
- **Calls:** WebRTC mesh up to **8** participants; TURN via metered.ca
- **Push:** FCM (Android) · desktop push deferred

## Security engines (shipped)

| Engine | Scope |
|--------|--------|
| 1–5 | Retention, E2E integrity, footprint, metadata, sessions |
| 8 — Signal Protocol | libsignal on installed clients (8.10 web WASM **retired**) |
| 9 — Translation privacy | On-device ML Kit (Android) |
| 10 — Desktop | Electron + libsignal Node (Windows + Mac) |

See `memory/SSC-ROADMAP.md` for gate status.

## Implemented (MVP + post-MVP)

- Core messaging, groups, stories, calls, 2FA, panic wipe, OAuth, contacts
- Capacitor Android APK with full Signal surfaces
- **Windows desktop installer** (Electron + libsignal)
- **Mac desktop** build config (`.dmg` on macOS)
- AGPL compliance artifacts

## Deferred / remaining (see roadmap)

- **Custom domain + Turnstile** (~28 Jun 2026)
- **Two-phone smoke + TURN verification** (founder manual)
- **Unified identity** — libsignal curve primary (3 testers)
- **Contacts graph privacy** — server-blind friend graph
- **SFU** for group calls 9+ (mediasoup · ~28 Jun with domain)
- **iOS** — deferred ($99/yr + Mac)

## Test health (2026-06-24)

- Backend pytest: **476 passed**, 1 skipped
- Engine 1–5, 8, 9, 10, AGPL gates: **PASS**
- Frontend `yarn test:ci`: **22 passed**
- `e2e_smoke.py`: **PASS**