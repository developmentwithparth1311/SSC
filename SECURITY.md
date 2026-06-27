# Security policy

## Reporting vulnerabilities

If you find a security issue in SSC, please **do not** open a public GitHub issue with exploit details.

1. Open a [GitHub Security Advisory](https://github.com/raullavita/SSC/security/advisories/new) (preferred), or
2. Email **contact@supersecurechat.com** with a clear description and reproduction steps.

We will acknowledge reports as soon as we can. Please allow time for a solo-maintainer project.

## What must never be committed

| Secret | Where it lives |
|--------|----------------|
| `MONGO_URL`, `JWT_SECRET`, `CONTACT_GRAPH_PEPPER` | `backend/.env`, `backend/cloud_run.env` |
| `GOOGLE_CLIENT_SECRET`, Firebase service account JSON | `backend/.env`, `backend/firebase/` |
| `TURNSTILE_SECRET`, `TURN_CREDENTIAL`, `VAPID_PRIVATE` | `backend/.env`, `cloud_run.env` |
| `REDIS_URL` (contains token) | `cloud_run.env` |
| Android release keystore | `frontend/android/keystore.properties`, `*.jks` |
| `google-services.json` | `frontend/android/app/` |
| Site preview / construction passwords | `frontend/.env.production.local` |
| Personal tester email lists | `scripts/firebase_testers.txt` |

Copy from `*.example` files only. If a secret was ever committed, **rotate it** (new JWT, DB password, OAuth secret, etc.) — removing from git history alone is not enough.

## Public vs private

- **Source code** is intended to be public (AGPL-3.0 + libsignal obligations on distributed APK).
- **Production credentials** stay on the maintainer's machine and in Cloud Run / Firebase console — not in the repo.
- **User message plaintext** is never stored on the server; user private keys are password-encrypted client-side before upload.

## Safe contribution areas

Help is welcome on: encryption flows, WebRTC signaling, Android/Electron libsignal, tests, i18n, accessibility, and documentation. Do not paste production URLs with tokens or personal emails in PRs.