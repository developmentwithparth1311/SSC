# Contributing to SSC

SSC is **install-only** (Android APK + Windows/Mac desktop). Browser-tab chat is intentionally blocked. See `InstalledClientGate.jsx`.

## How to help (no payment expected — thank you)

1. **Fork** the repo and open a **Pull Request** with a focused change.
2. Or open an **Issue** describing a bug with steps to reproduce (no production secrets in issues).
3. Read `memory/SECURITY_MODEL.md` and `memory/SSC-ROADMAP.md` for architecture context.

## Local setup (summary)

```powershell
docker compose up -d
cd backend && python -m venv venv && .\venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # fill MONGO_URL, JWT_SECRET
cd ..\frontend && yarn install && copy .env.example .env
```

See `README.md` for LAN APK and desktop builds.

## Before you PR

- Run `cd frontend && yarn test:ci`
- Run `cd backend && .\venv\Scripts\python.exe -m pytest tests/ -q` (with local API if integration tests apply)
- No secrets, personal emails, or home LAN IPs in the diff
- Match existing code style; small PRs are easier to review

## License

By contributing, you agree your contributions are licensed under the same terms as the project (AGPL-3.0). See `LICENSE`.