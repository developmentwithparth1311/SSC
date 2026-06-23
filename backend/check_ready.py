"""Local readiness check — prints PASS/FAIL only, never secrets."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND = Path(__file__).resolve().parent
ROOT = BACKEND.parent


def main() -> int:
    checks: list[tuple[str, bool]] = []

    def ok(name: str, cond: bool) -> None:
        checks.append((name, cond))

    ok("Firebase service account file", (BACKEND / "firebase/service-account.json").is_file())
    ok("google-services.json (Android)", (ROOT / "frontend/android/app/google-services.json").is_file())
    ok("GOOGLE_APPLICATION_CREDENTIALS set", bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")))
    cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    ok("Service account path exists", Path(cred).is_file() if cred else False)
    ok("MONGO_URL set", bool(os.getenv("MONGO_URL")))
    ok("JWT_SECRET set", bool(os.getenv("JWT_SECRET")))

    import native_push

    ok("Firebase Admin SDK loads", native_push.is_configured())

    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {name}")

    print("---")
    ready = all(c[1] for c in checks)
    print("READY" if ready else "NOT READY")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())