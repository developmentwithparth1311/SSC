# SSC Roadmap v2

## Status

This roadmap replaces the prior roadmap and reflects the new product direction.

## Product Goal

Build a professional, simple, privacy-first ephemeral messaging app that feels like WhatsApp or Telegram, but with:
- 24-hour retention by default
- configurable retention options
- no vault UI
- universal libsignal encryption
- strong panic wipe behavior
- public hosting with a real domain

---

## Phase 1 — Product reset

### Goals
- define the new product vision clearly
- remove vault-like and confusing security language from the user experience
- align the app around ephemeral messaging as the core product promise

### Deliverables
- [x] product blueprint documented
- [ ] remove old vault-centric UX flows
- [ ] simplify onboarding and login flow
- [ ] decide final retention defaults and options

---

## Phase 2 — Core auth and onboarding

### Goals
- make registration and login simple and robust
- support username + email/password and Google sign-in
- make the first-run experience feel polished

### Deliverables
- [ ] username-based registration flow
- [ ] email/password login/register flow
- [ ] Google authentication flow
- [ ] polished onboarding UI

---

## Phase 3 — Ephemeral messaging foundation

### Goals
- make chat content temporary by default
- ensure messages and files expire automatically
- store content in a way that supports clean deletion

### Deliverables
- [ ] retention timer model
- [ ] default 24-hour expiry
- [ ] user-configurable retention options
- [ ] server-side expiration enforcement
- [ ] automatic cleanup jobs

---

## Phase 4 — Encryption and security model

### Goals
- make libsignal the default encryption standard everywhere
- remove partial or alternate encryption paths in the user experience
- keep the app simple for end users

### Deliverables
- [ ] libsignal-based encryption for chats
- [ ] libsignal-based file protection
- [ ] libsignal-based call signaling
- [ ] panic wipe implementation

---

## Phase 5 — Panic wipe and session reset

### Goals
- make emergency wipe feel reliable and complete
- force logout and login re-entry after panic wipe

### Deliverables
- [ ] local content purge
- [ ] server-side content purge
- [ ] session invalidation
- [ ] forced re-authentication after wipe

---

## Phase 6 — UI polish

### Goals
- make the app feel professional and organic
- remove technical clutter and extra options
- align the app with WhatsApp/Telegram-like expectations

### Deliverables
- [ ] simplified settings
- [ ] cleaner navigation
- [ ] reduced advanced security clutter
- [ ] improved onboarding polish

---

## Phase 7 — Production hosting

### Goals
- move the app from local/dev assumptions to public hosting
- support a real domain and HTTPS

### Deliverables
- [ ] choose hosting stack
- [ ] buy domain
- [ ] configure DNS and HTTPS
- [ ] deploy frontend and backend
- [ ] configure storage and push

---

## Phase 8 — Beta release

### Goals
- validate real-device messaging and panic wipe flows
- verify retention behavior end to end
- confirm calls and media cleanup work correctly

### Deliverables
- [ ] two-device messaging test
- [ ] file expiry validation
- [ ] call artifact cleanup validation
- [ ] beta testing round

---

## Notes

This roadmap is intentionally focused on the new product shape and does not preserve the old roadmap assumptions.
