# SSC — Super Secure Chat

Hybrid full-stack E2E-encrypted ephemeral messaging (WhatsApp/Telegram-style, self-hosted).

**Core features:** 24h auto-delete · client-side E2E (RSA-OAEP + AES-256-GCM) · auto-translation · voice/video calls · stories · panic wipe · groups · read receipts · typing · PWA + native push (FCM)

**Current focus:** solo LAN testing (PC backend + phone APK). Production HTTPS deploy deferred until budget allows.

## Quick start (Windows, LAN dev)

### 1. Data layer

```powershell
cd SSC-main
docker compose up -d          # Mongo + Redis
```

### 2. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env        # set MONGO_URL, JWT_SECRET
.\venv\Scripts\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000
```

API: `http://<your-pc-lan-ip>:8000` (e.g. `http://192.168.1.154:8000`)

### 3. Frontend (PC browser)

```powershell
cd frontend
yarn install
copy .env.example .env        # REACT_APP_BACKEND_URL=http://localhost:8000
yarn start
```

### 4. Phone APK (same Wi‑Fi as PC)

Edit `frontend/package.json` `build:phone` script with your PC LAN IP, or set env before build:

```powershell
cd frontend
$env:REACT_APP_BACKEND_URL="http://192.168.1.154:8000"
yarn build:phone
npx cap sync android
cd android; .\gradlew assembleDebug
```

APK: `frontend/android/app/build/outputs/apk/debug/app-debug.apk`

Phones must reach the backend on port **8000** (firewall: allow inbound on private network).

### 5. Windows desktop (production API + libsignal)

```powershell
.\SSC-BUILD-DESKTOP-WIN.bat
```

Installer: `frontend/desktop/dist/SSC-Setup-1.0.0.exe`

Mac `.dmg`: run `SSC-BUILD-DESKTOP-MAC.sh` on macOS (see `memory/DESKTOP_CLIENT_CHARTER.md`).

## Project location (fixed — do not move)

| Role | Path |
|------|------|
| **Code repo** | `C:\Users\smash\SSC-main` |
| **Desktop shortcuts + Firebase APK folder** | `C:\Users\smash\Desktop\SSC` |

See `memory/PROJECT_LOCATION.md` for the full policy. The repo is not duplicated on the Desktop — only launchers and upload copies live there.

## Project structure

```
SSC-main/
├── backend/           # FastAPI + Motor (MongoDB) + WebSockets
│   ├── server.py
│   ├── core/          # config, auth, db, models, translation, push
│   ├── routers/       # auth, messages, contacts, invites, panic, …
│   └── tests/
├── frontend/          # React 19 + CRA/craco + Tailwind + Capacitor
│   ├── src/
│   │   ├── lib/i18n.js          # EN / ES / RO UI strings
│   │   ├── context/LocaleContext.jsx
│   │   └── pages/ChatHome.jsx   # main chat UI
│   └── android/                 # Capacitor Android project
├── docker-compose.yml
└── memory/PRD.md
```

## What's implemented (recent)

| Area | Status |
|------|--------|
| Search-first add contacts (ADD tab, username search) | Done |
| Auto-translation (MyMemory, same-lang skip, vault unlock required) | Done |
| Panic wipe (erases chats/files, keeps account, logs out) | Done |
| Full app UI language (EN / ES / RO) | Done |
| Mobile UI polish (single-pane, safe areas, composer) | Done |
| Native splash + dark status bar (Capacitor) | Done |
| Google OAuth (PC web; phone needs HTTPS) | Partial |
| Turnstile captcha | Optional / deferred on LAN |
| HTTPS production deploy | Deferred |

## Roadmap

| Done | Next |
|------|------|
| i18n, native splash/status bar, git + docs | **Translation quality** (long messages) |
| | HTTPS deploy (when budget allows) |
| | Play Store / domain |
| | Turnstile in production |

## Environment files

| File | Purpose |
|------|---------|
| `backend/.env.example` | Mongo, JWT, CORS, translation, TURN, VAPID, Google OAuth, FCM |
| `frontend/.env.example` | `REACT_APP_BACKEND_URL`, Turnstile, VAPID |
| `frontend/.env.mobile.example` | Template for HTTPS production mobile builds |

Copy examples to `.env` — **never commit** `.env`, `google-services.json`, or Firebase service account JSON.

### LAN CORS tip

Add your dev origins to `backend/.env`:

```
CORS_ORIGINS=http://localhost:3000,http://192.168.1.154:3000,http://192.168.1.154:8000
```

## Roadmap & security

- **Single roadmap:** `memory/SSC-ROADMAP.md` (update after every step)
- **Security model:** `memory/SECURITY_MODEL.md`

## Testing

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v
```

~81 tests pass (1 Google OAuth test may fail if OAuth credentials are not configured).

## Mobile (Capacitor)

- **Web/PWA** unchanged — `yarn start`, service worker push on HTTPS
- **Native push** — FCM via `@capacitor/push-notifications` + Firebase Admin on backend
- Place `google-services.json` in `frontend/android/app/` locally (gitignored)
- Place Firebase service account in `backend/firebase/` locally (gitignored)
- Splash: branded dark screen, fades out after app bootstrap
- Status bar: dark `#0A0A0A`, does not overlay content on Android

```powershell
yarn cap:sync      # build:phone + copy to android/
yarn cap:android     # open Android Studio
```

## Production checklist (when ready)

1. `ENV=production`, strong `JWT_SECRET`
2. `CORS_ORIGINS` = real frontend URL(s) only
3. **HTTPS** everywhere (required for Web Crypto on mobile, Google login on phone, PWA push)
4. Redis for shared rate limits: `docker compose up -d redis`
5. Turnstile + VAPID keys
6. TURN server for cross-network WebRTC
7. Monitor `GET /api/health`

## Git

```powershell
cd SSC-main
git init
git add .
git commit -m "Initial commit: SSC chat app"
```

Remote (when you have a repo):

```powershell
git remote add origin https://github.com/raullavita/SSC.git
git push -u origin main
```

## Common issues

| Problem | Fix |
|---------|-----|
| Phone can't reach API | Same Wi‑Fi, correct LAN IP in `build:phone`, Windows firewall port 8000 |
| `python` opens Store | Install Python from python.org; disable App Installer alias |
| Mongo errors | `docker compose up -d` or check `MONGO_URL` |
| Translation unchanged | Both users same language → UI hides auto-translate; unlock vault first |
| Google login on phone | Needs HTTPS deploy (deferred) |
| Calls fail off-LAN | Add TURN credentials in `backend/.env` |

## Design & spec

- `design_guidelines.json` — dark tactical theme
- `memory/PRD.md` — full product requirements