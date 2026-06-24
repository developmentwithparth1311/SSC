# SSC project location — do not move

**Canonical code repo (only place with source, git, builds, secrets):**

```
C:\Users\smash\SSC-main
```

| What | Path |
|------|------|
| Git / GitHub | `C:\Users\smash\SSC-main` |
| Backend + `.env` | `C:\Users\smash\SSC-main\backend` |
| Frontend + Android | `C:\Users\smash\SSC-main\frontend` |
| Roadmap (single truth) | `C:\Users\smash\SSC-main\memory\SSC-ROADMAP.md` |
| Fresh APK (after build) | `C:\Users\smash\SSC-main\frontend\android\app\build\outputs\apk\debug\app-debug.apk` |
| Windows installer | `C:\Users\smash\SSC-main\frontend\desktop\dist\SSC-Setup-1.0.0.exe` |

**Desktop control panel (shortcuts + uploads — not a second copy of the repo):**

```
C:\Users\smash\Desktop\SSC
```

| Subfolder | Purpose |
|-----------|---------|
| `Launchers\` | Double-click `.bat` files — all run commands inside `SSC-main` |
| `APK\` | Copy of latest APK for Firebase upload (`SSC-app-debug.apk`) |
| `Keys\` | Backup copies of OAuth / Firebase JSON (live files stay in `SSC-main`) |
| `Docs\` | Pointers and notes — canonical docs are in `SSC-main\memory\` |
| `Archive\` | Old zips and screenshots only |

## Rules

1. **Never clone or unzip a second `SSC-main`** into Desktop, Downloads, or elsewhere.
2. **Never edit code** under `Desktop\SSC` — there is no code there.
3. **Open Cursor / Grok** on `C:\Users\smash\SSC-main` (or parent `C:\Users\smash`).
4. After `SSC-BUILD-APK.bat`, upload from `Desktop\SSC\APK\` or the build output path above (same file).
5. If you must relocate the machine, move **only** `C:\Users\smash\SSC-main` and update `Desktop\SSC\Launchers\` paths once.

## Why two folders?

- `SSC-main` = real project (version control, dependencies, Cloud Run deploy).
- `Desktop\SSC` = your dashboard on the desktop (one-click start, Firebase upload folder).

Both are intentional. The app does **not** break from having Desktop shortcuts as long as the repo stays at `C:\Users\smash\SSC-main`.