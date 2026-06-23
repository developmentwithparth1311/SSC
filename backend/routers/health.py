"""Health check routes."""
from fastapi import APIRouter, Response

from core.health_checks import full_health
from core.utils import iso, now_utc

router = APIRouter()


@router.get("/")
async def root():
    return {"app": "SSC", "status": "ok", "time": iso(now_utc())}


@router.get("/health")
async def health(response: Response):
    """Detailed probe for load balancers / uptime monitors."""
    body = await full_health()
    if body["status"] == "error":
        response.status_code = 503
    return body