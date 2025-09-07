# app/services/categorize_service.py

import asyncio
from app.db.pool import get_pool
#from app.services.categorization.py import categorize_transaction
from app.schemas import CategorizeResponse


async def categorize_transaction(tx: dict) -> dict:
    # Basic logic — replace with actual LLM call if needed
    description = tx["description"].lower()
    amount = tx["amount"]

    category = "travel" if "uber" in description else "uncategorized"
    confidence = 0.85
    needs_review = confidence < 0.9

    return {
        "id": tx["id"],
        "user_id": tx["user_id"],
        "category": category,
        "confidence": confidence,
        "needs_review": needs_review,
        "prompt": f"Categorize: {tx['description']} (£{amount})",
        "response": f"Category: {category}, Confidence: {confidence}",
        "source_model": "mistral-7b"
    }



async def run_categorization_pipeline() -> CategorizeResponse:
    pool = await get_pool()

    # Step 1: Fetch uncategorized transactions
    async with pool.acquire() as conn:
        transactions = await conn.fetch("""
            SELECT id, description, amount, user_id
            FROM transactions
            WHERE category IS NULL
        """)

    # Step 2: Run LLM categorization in parallel
    updates = await asyncio.gather(*(categorize_transaction(tx) for tx in transactions))
    updates = [u for u in updates if u]

    # Step 3: Apply updates and log interactions
    async with pool.acquire() as conn:
        async with conn.transaction():
            for u in updates:
                await conn.execute("""
                    UPDATE transactions
                    SET category=$1, confidence=$2, needs_review=$3
                    WHERE id=$4
                """, u["category"], u["confidence"], u["needs_review"], u["id"])

                await conn.execute("""
                    INSERT INTO conversation_logs (
                        user_id, input_text, llm_response, task_type, source_model
                    ) VALUES ($1, $2, $3, $4, $5)
                """, u.get("user_id", "system"), u["prompt"], u["response"], "categorization", u["source_model"])

    # Step 4: Return structured response
    return CategorizeResponse(
        status="success",
        transactions=updates,
        low_confidence_count=sum(1 for u in updates if u["needs_review"])
    )

