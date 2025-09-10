from app.db.pool import get_pool
from app.services.categorize_service import categorize_transaction
import asyncio

async def categorize_new_transactions():
    pool = await get_pool()
    async with pool.acquire() as conn:
        transactions = await conn.fetch("""
            SELECT id, user_id, description, amount
            FROM transactions
            WHERE tax_category IS NULL OR tax_category = 'Uncategorized'
        """)
        #print("Transactions received for categorization:", transactions)

    updates = await asyncio.gather(*(categorize_transaction(tx) for tx in transactions))    
    updates = [u for u in updates if u]

    async with pool.acquire() as conn:
        async with conn.transaction():
            for u in updates:
                await conn.execute("""
                    UPDATE transactions
                    SET tax_category=$1, confidence=$2, needs_review=$3
                    WHERE id=$4
                """, u["tax_category"], u["confidence"], u["needs_review"], u["id"])