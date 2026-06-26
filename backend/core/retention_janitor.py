"""Background retention janitor for file metadata and GridFS blob cleanup.

L.1 goal: enforce server-side purge beyond Mongo TTL by removing orphaned
GridFS blobs and marking/deleting expired file records.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

from core.database import db as default_db, grid_fs as default_grid_fs
from core.files import delete_file_gridfs
from core.logging_config import logger
from core.logging_policy import safe_exception_label
from core.security_observability import security_event
from core.utils import iso, now_utc

_janitor_task: Optional[asyncio.Task] = None


@dataclass
class JanitorRunReport:
    scanned_expired_file_records: int = 0
    marked_deleted_file_records: int = 0
    deleted_gridfs_for_expired_records: int = 0
    scanned_gridfs_blobs: int = 0
    orphaned_gridfs_blobs_deleted: int = 0
    errors: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def janitor_enabled() -> bool:
    raw = (os.environ.get("SSC_RETENTION_JANITOR_ENABLED") or "true").strip().lower()
    return raw not in {"0", "false", "off", "no"}


def janitor_interval_seconds() -> int:
    raw = (os.environ.get("SSC_RETENTION_JANITOR_INTERVAL_SECONDS") or "300").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 300
    return max(30, min(value, 3600))


def janitor_batch_size() -> int:
    raw = (os.environ.get("SSC_RETENTION_JANITOR_BATCH_SIZE") or "250").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 250
    return max(10, min(value, 2000))


async def _delete_expired_file_records(database, report: JanitorRunReport, *, now: datetime, batch_size: int) -> None:
    cursor = database.files.find(
        {
            "is_deleted": {"$ne": True},
            "expires_at": {"$exists": True, "$lt": now},
        },
        {"_id": 0, "file_id": 1},
    ).limit(batch_size)

    async for row in cursor:
        report.scanned_expired_file_records += 1
        file_id = row.get("file_id")
        if not file_id:
            report.errors += 1
            continue
        try:
            await delete_file_gridfs(file_id)
            report.deleted_gridfs_for_expired_records += 1
        except Exception as exc:
            report.errors += 1
            logger.warning(
                f"retention-janitor expired file gridfs delete failed file={file_id}: "
                f"{safe_exception_label(exc)}"
            )
        try:
            res = await database.files.update_one(
                {"file_id": file_id, "is_deleted": {"$ne": True}},
                {"$set": {"is_deleted": True, "deleted_at": iso(now_utc())}},
            )
            if res.modified_count:
                report.marked_deleted_file_records += 1
        except Exception as exc:
            report.errors += 1
            logger.warning(
                f"retention-janitor file record mark deleted failed file={file_id}: "
                f"{safe_exception_label(exc)}"
            )


async def _delete_orphan_gridfs_blobs(database, gridfs_bucket, report: JanitorRunReport, *, batch_size: int) -> None:
    cursor = database["ssc_files.files"].find({}, {"_id": 1, "filename": 1}).limit(batch_size)

    async for blob in cursor:
        report.scanned_gridfs_blobs += 1
        blob_id = blob.get("_id")
        filename = blob.get("filename")
        if not blob_id or not filename:
            report.errors += 1
            continue

        owner = await database.files.find_one(
            {
                "file_id": filename,
                "is_deleted": {"$ne": True},
            },
            {"_id": 1},
        )
        if owner:
            continue

        try:
            await gridfs_bucket.delete(blob_id)
            report.orphaned_gridfs_blobs_deleted += 1
        except Exception as exc:
            report.errors += 1
            logger.warning(
                f"retention-janitor orphan gridfs delete failed file={filename}: "
                f"{safe_exception_label(exc)}"
            )


async def run_retention_janitor_once_with_handles(database, gridfs_bucket) -> JanitorRunReport:
    now = datetime.now(timezone.utc)
    batch_size = janitor_batch_size()
    report = JanitorRunReport()

    await _delete_expired_file_records(database, report, now=now, batch_size=batch_size)
    await _delete_orphan_gridfs_blobs(database, gridfs_bucket, report, batch_size=batch_size)

    if any(
        (
            report.marked_deleted_file_records,
            report.deleted_gridfs_for_expired_records,
            report.orphaned_gridfs_blobs_deleted,
            report.errors,
        )
    ):
        logger.info(
            "retention-janitor run: "
            f"expired_scanned={report.scanned_expired_file_records} "
            f"records_deleted={report.marked_deleted_file_records} "
            f"gridfs_deleted={report.deleted_gridfs_for_expired_records} "
            f"gridfs_scanned={report.scanned_gridfs_blobs} "
            f"orphan_blobs_deleted={report.orphaned_gridfs_blobs_deleted} "
            f"errors={report.errors}"
        )

    if report.orphaned_gridfs_blobs_deleted:
        security_event(
            "retention_orphan_gridfs_deleted",
            severity="warning",
            deleted=report.orphaned_gridfs_blobs_deleted,
            scanned=report.scanned_gridfs_blobs,
        )
    if report.errors:
        security_event(
            "retention_janitor_errors",
            severity="error",
            count=report.errors,
        )

    return report


async def run_retention_janitor_once() -> JanitorRunReport:
    return await run_retention_janitor_once_with_handles(default_db, default_grid_fs)


async def start_retention_janitor() -> None:
    global _janitor_task

    if _janitor_task is not None:
        return
    if not janitor_enabled():
        logger.info("retention-janitor disabled by SSC_RETENTION_JANITOR_ENABLED")
        return

    interval = janitor_interval_seconds()

    async def _loop() -> None:
        while True:
            try:
                await run_retention_janitor_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning(f"retention-janitor loop error: {safe_exception_label(exc)}")
            await asyncio.sleep(interval)

    _janitor_task = asyncio.create_task(_loop())
    logger.info(f"retention-janitor started interval={interval}s batch={janitor_batch_size()}")


async def stop_retention_janitor() -> None:
    global _janitor_task

    if _janitor_task is None:
        return

    _janitor_task.cancel()
    try:
        await _janitor_task
    except asyncio.CancelledError:
        pass
    finally:
        _janitor_task = None
