# Engine 6 — Push & own-metal evaluation charter

**Version:** 1.0  
**Effective:** 2026-06-24  
**Engine:** 6 — Push / own-metal  
**Status:** Evaluation complete · implementation deferred where noted

---

## 1. Purpose

Engine 6 decides **what stays on free/managed services** vs **what moves to founder-owned metal** after scale or investment — without blocking current tester rollout.

This charter records the **evaluation outcome** (not full migration).

---

## 2. Push path evaluation (complete)

| Path | Verdict | Notes |
|------|---------|-------|
| **FCM (Android APK)** | ✅ Keep | Firebase `super-chat-b0992` · App Distribution + native push · free tier sufficient for testers |
| **Web VAPID push** | ✅ Keep | Self-generated keys · no third-party push vendor on web |
| **UnifiedPush / ntfy self-host** | ⬜ Deferred | Adds ops burden; revisit if FCM policy/billing forces exit |
| **APNs direct (iOS)** | ⬜ Deferred | Requires Apple Developer ($99/yr) — ties to iOS Capacitor P2 item |

**Decision:** Production push stays **FCM + VAPID**. No self-hosted push broker until tester scale or policy requires it.

---

## 3. Own-metal data layer evaluation (complete)

| Component | Current | Verdict | Notes |
|-----------|---------|---------|-------|
| **MongoDB** | Atlas `ssc` | ⬜ Deferred post-investors | TTL + retention engines enforce ephemeral model on Atlas today |
| **Redis** | Upstash | ✅ Keep for now | Rate limits, session revocation, WS pub-sub fan-out |
| **API compute** | Cloud Run | ✅ Keep | HTTPS + autoscale; multi-worker needs Redis WS fan-out (P2) |
| **Firebase** | Auth push + distribution | ✅ Keep | Not on critical E2E path |

**Decision:** Own-metal Mongo/API **deferred** until budget/investors. Atlas + Cloud Run + Upstash is acceptable for founder + Firebase testers phase.

---

## 4. Engine 6 steps

| Step | Description | Status |
|------|-------------|--------|
| 6.1 | Push path evaluation charter | ✅ |
| 6.2 | Own-metal Mongo evaluation | ✅ (deferred — documented) |
| 6.3 | Own-metal migration runbook | ⬜ Post-investors |

---

## 5. Gate

Engine 6 gate = policy module + this charter + tests in `tests/test_engine6_policy.py`.

Full own-metal cutover is **out of scope** until step 6.3 is scheduled.