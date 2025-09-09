# app/services/categorize_service.py

import asyncio
from app.db.pool import get_pool
from app.schemas import CategorizeResponse
#from app.services.categorize_service import categorize_transaction




# Define keyword-based rules
KEYWORD_RULES = {
    "uber": "Travel & Mileage",
    "slack": "Software & Subscriptions",
    "hmrc": "HMRC Payments",
    "google ads": "Marketing & Advertising",
    "xero": "Software & Subscriptions",
    "rent": "Rent & Lease",
    "electricity": "Utilities",
    "insurance": "Insurance",
    "stationery": "Office Supplies"
}

# Confidence thresholds
HIGH_CONFIDENCE = 1.0
LOW_CONFIDENCE = 0.7

async def categorize_transaction(tx: dict) -> dict:
    description = tx["description"].lower()
    amount = tx["amount"]
    plaid_category = tx.get("plaid_category", "").lower()
    user_id = tx["user_id"]
    tx_id = tx["id"]

    pool = await get_pool()
    tax_category = "Uncategorized"
    deductible = True
    vat_applicable = True
    confidence = LOW_CONFIDENCE

    # Step 1: Keyword match
    for keyword, category in KEYWORD_RULES.items():
        if keyword in description:
            category = category
            confidence = HIGH_CONFIDENCE
            break

    # Step 2: Fallback to category_mappings
    if confidence < HIGH_CONFIDENCE and plaid_category:
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT tax_category, deductible, vat_applicable
                FROM category_mappings
                WHERE LOWER(plaid_category) = $1
                LIMIT 1
            """, plaid_category)
            if result:
                tax_category = result["tax_category"]
                deductible = result["deductible"]
                vat_applicable = result["vat_applicable"]
                confidence = 0.9

    needs_review = confidence < 0.9

    return {
        "id": tx_id,
        "user_id": user_id,
        "tax_category": tax_category,
        "deductible": deductible,
        "vat_applicable": vat_applicable,
        "confidence": confidence,
        "needs_review": needs_review,
        "prompt": f"Categorize: {tx['description']} (£{amount})",
        "response": f"Tax Category: {tax_category}, Confidence: {confidence}",
        "source_model": "local-rule-engine"
    }


async def run_categorization_pipeline() -> CategorizeResponse:
    pool = await get_pool()

    # Step 1: Fetch uncategorized transactions
    async with pool.acquire() as conn:
        transactions = await conn.fetch("""
            SELECT id, description, amount, user_id, plaid_category
            FROM transactions
            WHERE tax_category IS NULL
        """)

    # Step 2: Run categorization in parallel
    updates = await asyncio.gather(*(categorize_transaction(tx) for tx in transactions))
    updates = [u for u in updates if u]

    # Step 3: Apply updates and log interactions
    async with pool.acquire() as conn:
        async with conn.transaction():
            for u in updates:
                await conn.execute("""
                    UPDATE transactions
                    SET tax_category=$1, confidence=$2, needs_review=$3,
                        deductible=$4, vat_applicable=$5
                    WHERE id=$6
                """, u["tax_category"], u["confidence"], u["needs_review"],
                     u["deductible"], u["vat_applicable"], u["id"])

                await conn.execute("""
                    INSERT INTO conversation_logs (
                        user_id, input_text, llm_response, task_type, source_model, timestamp
                    ) VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
                """, u.get("user_id", "system"), u["prompt"], u["response"],
                     "categorization", u["source_model"])

    # Step 4: Return structured response with summary
    low_confidence_count = sum(1 for u in updates if u["needs_review"])
    summary_text = f"{len(updates)} transactions categorized, {low_confidence_count} flagged for review"

    return CategorizeResponse(
        status="success",
        transactions=updates,
        low_confidence_count=low_confidence_count,
        summary=summary_text
    )