from fastapi import APIRouter
from app.db.pool import get_pool
from app.schemas import CategorizeResponse
from app.services.categorization import categorize_transaction
import asyncio

router = APIRouter()

@router.post("/categorize", response_model=CategorizeResponse)
async def categorize_transactions():
    pool = await get_pool()
    async with pool.acquire() as conn:
        transactions = await conn.fetch("SELECT id, description, amount FROM transactions WHERE category IS NULL")

    updates = await asyncio.gather(*(categorize_transaction(tx) for tx in transactions))
    updates = [u for u in updates if u]

    async with pool.acquire() as conn:
        async with conn.transaction():
            for u in updates:
                await conn.execute("""
                    UPDATE transactions
                    SET category=$1, confidence=$2, needs_review=$3
                    WHERE id=$4
                """, u["category"], u["confidence"], u["needs_review"], u["id"])

    return CategorizeResponse(
        status="success",
        transactions=updates,
        low_confidence_count=sum(1 for u in updates if u["needs_review"])
    )