# app/routers/health.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health Checks"]
)

@router.get("/ping", summary="Basic health check for Server D")
def health_check():
    """
    Returns a simple status message to confirm the server is alive.

    Useful for startup diagnostics, orchestration validation, and uptime monitoring.
    """
    return {"status": "ok"}