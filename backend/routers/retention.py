"""Retention attestation endpoints."""
from fastapi import APIRouter, Depends

from core.auth import get_current_user
from core.database import db
from core.retention import retention_hours
from core.retention_proof import run_retention_proof
from core.utils import iso, now_utc

router = APIRouter(prefix="/retention")


@router.get("/attestation")
async def retention_attestation(_current=Depends(get_current_user)):
    report = await run_retention_proof(db, fail_on_expired=False, include_orphan_gridfs=True)
    return {
        "generated_at": iso(now_utc()),
        "retention_hours": retention_hours(),
        "report": report.to_dict(),
    }
