# SSC Product Blueprint v2

## Vision

SSC is a simple, professional, privacy-first messaging app designed around one core promise:

- chats, files, calls, and video calls are temporary by default
- everything expires automatically after a retention window
- users do not see security complexity, vaults, or technical setup screens
- the experience must feel like WhatsApp or Telegram, but more focused and more private

This version is not a technical demo. It is a real consumer messaging product.

---

## Product Principles

1. Ephemeral by default
   - 24-hour retention is the default
   - the user can change the retention duration later
   - messages, files, calls, and media should not live forever

2. No vault, no clutter
   - no vault UI
   - no exposed keys or security jargon
   - no confusing advanced settings for normal users

3. Simple onboarding
   - username
   - email and password, or Google sign-in
   - no phone-number requirement
   - minimal setup friction

4. Panic wipe is a serious emergency feature
   - erase local and server-side content
   - log the user out immediately
   - force login again on reopen

5. Encryption must be universal
   - libsignal-based encryption for text, media, groups, and call signaling
   - no partial or fallback-only encryption paths

6. Professional product experience
   - clean interface
   - low cognitive load
   - fast, reliable, minimal friction

---

## Core Experience

### Registration and login

Users should be able to:
- create an account with username + email + password
- sign in with Google
- recover quickly and simply

The onboarding experience should be short and focused.

### Main chat experience

The app should feel like a modern messaging app:
- conversations list
- one-tap chat entry
- text messaging
- image and file sharing
- voice and video calls
- status/stories if desired later

### Retention model

Default retention:
- 24 hours for chats and files
- 24 hours for calls and video-call artifacts
- expiration should be enforced both at the app layer and in storage

User options:
- 1 hour
- 6 hours
- 24 hours
- 7 days
- custom duration later if needed

### Panic wipe

The panic wipe flow must:
- delete local chats, media, cached content, and call artifacts
- delete server-side message and file content where applicable
- clear session state
- log the user out
- force the app to require login again on next launch

---

## Technical Direction

### Authentication

Recommended stack:
- email/password auth
- Google OAuth
- username-based identity
- secure session handling

### Encryption

The app should use libsignal as the primary and default encryption engine for:
- direct messages
- group messages
- file encryption
- call signaling
- call metadata protection

No vault-based design should be used in the new product flow.

### Data lifecycle

The app should be designed around short-lived content.

Persistent data:
- user account
- profile info
- contacts and blocks
- settings
- auth/session state

Ephemeral data:
- message text content
- file payloads
- attachments
- call recordings or call artifacts
- temporary media

All ephemeral data should have:
- created_at
- expires_at
- deletion status
- cleanup job support

### Storage architecture

Recommended architecture:
- MongoDB Atlas for account and metadata storage
- object storage such as Cloudflare R2 or AWS S3 for encrypted media/files
- Firebase only where useful for auth/push, not as the main content store

### Hosting

Recommended public hosting stack:
- domain via Cloudflare DNS
- frontend hosting on Vercel or Netlify
- backend API on Railway, Render, DigitalOcean, or Cloud Run
- file storage on Cloudflare R2 or S3
- push notifications via Firebase Cloud Messaging

The app should not be hosted locally for production.

---

## Data Model Direction

### Users
- id
- username
- email
- password hash or OAuth id
- profile info
- created_at
- last_seen
- settings

### Contacts
- user_id
- contact_user_id
- status
- blocked flag
- created_at

### Conversations
- id
- participants
- type
- created_at
- last_activity

### Messages
- id
- conversation_id
- sender_id
- body_ciphertext
- encrypted_media_ref
- created_at
- expires_at
- deleted_at
- status

### Files / media
- id
- message_id
- storage_key
- mime_type
- size
- encrypted flag
- created_at
- expires_at

### Calls
- id
- participants
- started_at
- ended_at
- expires_at
- session metadata

---

## UX / Design Direction

The experience should be:
- clean
- calm
- familiar
- low-friction
- minimal

The interface should avoid:
- coded-looking panels
- security jargon
- too many toggles
- confusing account settings

Primary design references:
- WhatsApp for conversation flow
- Telegram for speed and simplicity
- but with a more privacy-first and ephemeral core

---

## 13 Pending Workstreams

1. Rebuild the product scope around ephemeral messaging by default
2. Remove vault-style behavior from the experience and product flow
3. Redesign onboarding for username + email/password + Google login
4. Rebuild auth and session handling for a polished consumer experience
5. Implement a universal libsignal encryption path for all messaging surfaces
6. Implement default 24-hour retention and configurable retention settings
7. Build automatic deletion for chats, files, and call artifacts in both app and backend
8. Rebuild panic wipe to fully erase local and server-side content and force logout
9. Simplify the UI to remove technical and advanced-security clutter
10. Rebuild the backend data model so message content is short-lived and not treated as permanent storage
11. Replatform hosting for production use with domain, HTTPS, and public deployment
12. Set up production storage and push infrastructure for files and notifications
13. Run real-device QA and close the founder-testing loop before wider rollout

---

## Recommended Next Move

The next phase should focus on a clean rebuild of the product around these rules:
- ephemeral messaging first
- simple onboarding
- no vault
- libsignal everywhere
- panic wipe as a core feature
- public hosting with a proper domain

This should become the new roadmap and the new product definition.
