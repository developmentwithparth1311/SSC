# SSC Security Model

**Version:** 1.0 · **Updated:** 2026-06-23  
**Audience:** Founder, testers, investors  
**Companion:** `memory/SSC-ROADMAP.md`

---

## 1. What SSC protects

| Asset | Protection |
|-------|------------|
| Message bodies | Client-side encryption before server; server stores ciphertext only |
| Files | E2E ciphertext in GridFS; conversation ACL on download |
| Private key | PBKDF2 + AES-GCM wrap; decrypted key in memory only (vault) |
| Sessions | HttpOnly cookie (web) or in-memory token (Android); Redis revocation in production |
| 24h recycle | Mongo TTL on messages, files, stories, conversations |

**Panic wipe:** Deletes chats, files, stories, sessions, device secrets. **Keeps** account + contacts.

---

## 2. Two encryption layers (important)

SSC currently runs **two systems in parallel** during migration:

| Layer | Algorithm | Used for |
|-------|-----------|----------|
| **Legacy RSA** | RSA-OAEP 2048 + AES-256-GCM per message | Web/PWA, groups, attachments, stories, old messages, account registration |
| **Signal `signal_v1`** | X3DH + Double Ratchet (libsignal 0.96.2) | Android APK: 1:1 text + 1:1 call signaling when both peers ready |

UI labels: **SIG** (green) vs **RSA** (yellow) on messages and composer hints.

---

## 3. Coverage by surface (today)

### Android APK (native libsignal)

| Surface | Encrypted? | Protocol |
|---------|------------|----------|
| 1:1 text | ✅ Ratchet | `signal_v1` when both peers have prekeys + session |
| 1:1 text fallback | ✅ E2E | `legacy_rsa` (peer not upgraded, no session) |
| 1:1 attachments | ✅ E2E | `legacy_rsa` only — **not ratchet yet** |
| Group messages | ✅ E2E | `legacy_rsa` per recipient — **no Sender Keys** |
| 1:1 call signaling (SDP/ICE) | ✅ Ratchet-wrapped | `signaling_protocol: signal_v1` |
| Group call signaling | ⚠️ Server relays cleartext SDP/ICE | Legacy (deferred) |
| Call media (audio/video) | ✅ P2P WebRTC | Encrypted by DTLS-SRTP between peers |

### Web / PWA

| Surface | Encrypted? | Protocol |
|---------|------------|----------|
| All messaging | ✅ E2E | `legacy_rsa` only — **no libsignal on web** |
| Call signaling | ⚠️ Cleartext on server relay | Legacy |

---

## 4. Should the whole app use Signal?

**Yes — that is the product goal.** Engine 8 shipped the **foundation and the hardest path** (official libsignal, prekey relay, X3DH, ratchet, dual-read, encrypted 1:1 call setup) without locking out existing users.

**Not yet on Signal (planned):**

1. 1:1 attachments  
2. Web/PWA clients  
3. Group messages (Sender Keys)  
4. Group call signaling  
5. Stories/statuses  

**Will stay RSA-based:** Account vault unlock (password → private key). That is identity/key-wrapping, not message transport — same pattern Signal uses for local PIN/biometric protection.

---

## 5. What the server can see

| Data | Server sees |
|------|-------------|
| `signal_v1` messages | Opaque ciphertext + `signal_message_type` |
| `legacy_rsa` messages | Ciphertext + IV + per-user wrapped keys |
| 1:1 call signaling (upgraded) | Opaque `signaling_ciphertext` only |
| Group call signaling | SDP + ICE (cleartext) |
| Contacts | Who is friends with whom (persistent) |
| Push | Generic body; routing metadata (tokens, conversation_id) |
| Translation (if enabled) | **Plaintext** — disabled by default |

---

## 6. Comparison to Signal & WhatsApp (honest)

| Capability | SSC (today) | Signal / WhatsApp |
|------------|-------------|-------------------|
| 1:1 text ratchet (Android) | ✅ Same class (libsignal) | ✅ |
| 1:1 text (web) | Legacy RSA | Full protocol |
| Groups | RSA wrap, not Sender Keys | Sender Keys |
| Attachments in protocol | RSA envelope | In-protocol |
| Sealed sender | ❌ | Signal ✅ |
| Multi-device | ❌ | ✅ |
| Default server deletion | 24h TTL (strong default) | Optional disappearing |
| Published audit | ❌ | Years of scrutiny |
| Global HTTPS prod | ✅ Cloud Run | ✅ |

**Marketing rule:** Say **"Signal-grade 1:1 chat on the Android app"** — not "entire app is Signal" until phases in roadmap are done.

---

## 7. Third-party & compliance

| Item | Status |
|------|--------|
| libsignal | Official `@signalapp` / `org.signal` only · **AGPL-3.0** — legal review before public Play |
| Google OAuth / FCM / Firebase | Configured · project `super-chat-b0992` |
| Mongo Atlas | Production database |
| Translation | MyMemory / Google — **opt-in E2E break** |

---

## 8. Production endpoints

- API: `https://ssc-api-4jp3wuccwa-ew.a.run.app`
- OAuth callback: `https://ssc-api-4jp3wuccwa-ew.a.run.app/api/auth/google/callback`
- APK must use Cloud Run URL (not LAN IP) for testers