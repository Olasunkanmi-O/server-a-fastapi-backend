from fastapi import APIRouter
from app.db.pool import get_pool
from app.schemas import ReviewResponse

router = APIRouter()

@router.get("/review", response_model=ReviewResponse)
async def review_low_confidence():
    pool = await get_pool()
    async with pool.acquire() as conn:
        results = await conn.fetch("""
            SELECT id, description, amount, category, confidence
            FROM transactions
            WHERE needs_review = TRUE
        """)
    return ReviewResponse(
        status="found",
        transactions=[dict(r) for r in results]
    )