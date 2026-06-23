"""Quick MongoDB connectivity test (uses cloud_run.env)."""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / "cloud_run.env")

try:
    import certifi
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as e:
    print(f"import error: {e}")
    sys.exit(1)


async def main() -> int:
    url = os.environ.get("MONGO_URL", "")
    if not url:
        print("MONGO_URL not set")
        return 1
    client = AsyncIOMotorClient(
        url,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=15000,
    )
    try:
        result = await client.admin.command("ping")
        print("PING OK:", result)
        return 0
    except Exception as e:
        print("PING FAILED:", type(e).__name__, str(e)[:500])
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))