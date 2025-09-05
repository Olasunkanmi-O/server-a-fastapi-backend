import time
import asyncio
from fastapi import FastAPI
from app.routers import categorize, scenario, review, health
from app.llm_service.db import close_db_pool, get_pool

start_time = time.time()
print(f"[Profiler] App startup initiated at {start_time:.2f}")

app = FastAPI(
    title="AI Financial Assistant",
    description="APIs for categorizing transactions, running scenarios, and reviewing low-confidence results",
    version="1.0.0"
)

# Log router inclusion
router_start = time.time()
app.include_router(categorize.router, prefix="/transactions", tags=["Categorize"])
app.include_router(scenario.router, prefix="/transactions", tags=["Scenario"])
app.include_router(review.router, prefix="/transactions", tags=["Review"])
app.include_router(health.router, prefix="/health", tags=["Health"])
print(f"[Profiler] Routers loaded in {time.time() - router_start:.2f}s")

# Background task
async def periodic_categorization():
    from app.routers.categorize import categorize_transactions
    while True:
        pool_start = time.time()
        pool = await get_pool()
        print(f"[Profiler] DB pool acquired in {time.time() - pool_start:.2f}s")
        await categorize_transactions({"transactions": [], "user_id": None})
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    print(f"[Profiler] Startup event triggered at {time.time() - start_time:.2f}s")
    asyncio.create_task(periodic_categorization())

@app.on_event("shutdown")
async def shutdown_event():
    print(f"[Profiler] Shutdown event triggered at {time.time() - start_time:.2f}s")
    await close_db_pool()

@app.get("/")
async def root():
    return {"message": "FiscalGuide LLM API is running!"}