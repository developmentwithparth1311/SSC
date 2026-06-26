"""MongoDB client, database, and GridFS bucket."""
import native_push as native_push_module
import push as push_module
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from core.config import DB_NAME, MONGO_URL, VAPID_EMAIL, VAPID_PRIVATE

push_module.VAPID_PRIVATE = VAPID_PRIVATE
push_module.VAPID_EMAIL = VAPID_EMAIL
native_push_module.db = None

try:
    import certifi
    if MONGO_URL.startswith("mongodb+srv://") or "tls=true" in MONGO_URL:
        client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
    else:
        client = AsyncIOMotorClient(MONGO_URL)
except Exception:
    client = AsyncIOMotorClient(MONGO_URL)

db = client[DB_NAME]
grid_fs = AsyncIOMotorGridFSBucket(db, bucket_name="ssc_files")
push_module.db = db
native_push_module.db = db