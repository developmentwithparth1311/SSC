"""GridFS file storage helpers."""
import uuid

from fastapi import HTTPException

from core.config import APP_NAME
from core.database import grid_fs


async def save_file_gridfs(data: bytes, filename: str, content_type: str) -> str:
    file_id = uuid.uuid4().hex
    await grid_fs.upload_from_stream(
        file_id,
        data,
        metadata={
            "content_type": content_type,
            "original_filename": filename,
            "app": APP_NAME,
        },
    )
    return file_id


async def load_file_gridfs(file_id: str):
    try:
        grid_out = await grid_fs.open_download_stream_by_name(file_id)
        data = await grid_out.read()
        ctype = (grid_out.metadata or {}).get("content_type") or "application/octet-stream"
        return data, ctype
    except Exception:
        raise HTTPException(404, "File not found or expired")


async def delete_file_gridfs(file_id: str) -> None:
    """Remove blob from GridFS by stream name (our file_id hex)."""
    from core.database import db

    doc = await db["ssc_files.files"].find_one({"filename": file_id}, {"_id": 1})
    if doc:
        await grid_fs.delete(doc["_id"])