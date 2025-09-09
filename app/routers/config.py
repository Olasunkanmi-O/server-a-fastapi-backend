from fastapi import APIRouter
from app.config import settings
from app.db.pool import get_pool
import asyncpg
import psutil
import time

router = APIRouter()
startup_time = time.time()

@router.get("/config")
async def show_config():
    # DB check
    db_status = "unknown"
    uncategorized_count = None
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
            db_status = "connected"
            uncategorized_count = await conn.fetchval("SELECT COUNT(*) FROM transactions WHERE tax_category IS NULL")
    except asyncpg.PostgresError:
        db_status = "error"

    # System stats
    process = psutil.Process()
    memory = process.memory_info().rss / (1024 * 1024)  # MB
    cpu = psutil.cpu_percent(interval=0.5)
    uptime = round(time.time() - startup_time)

    return {
        # "provider": settings.LLM_PROVIDER,
        # "model": "gpt-4o-mini" if settings.LLM_PROVIDER == "openai" else "custom",
        # "api_key_loaded": (
        #     bool(settings.OPENAI_API_KEY) if settings.LLM_PROVIDER == "openai"
        #     else bool(settings.GEMINI_API_KEY)
        # ),
        "database": {
            "url": settings.DATABASE_URL,
            "status": db_status,
            "uncategorized_transactions": uncategorized_count
        },
        "system": {
            "uptime_seconds": uptime,
            "memory_usage_mb": round(memory, 2),
            "cpu_usage_percent": cpu
        },
        "env": {
            "PLAID_CLIENT_ID": settings.PLAID_CLIENT_ID,
            "PLAID_ENV": settings.PLAID_ENV
        },
        "tasks": {
            "categorization": "running every 60s (stubbed)"
        }
    }
