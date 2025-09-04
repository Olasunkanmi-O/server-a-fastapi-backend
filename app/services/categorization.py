from app.providers.factory import get_provider
from app.config import settings

provider = get_provider(settings.LLM_PROVIDER)
CONFIDENCE_THRESHOLD = 0.8

async def categorize_transaction(tx):
    prompt = f"Categorize this transaction: '{tx['description']}' Amount: £{tx['amount']}"
    try:
        res = provider.generate_response(prompt)
        category = res.get("category", "Uncategorized")
        confidence = res.get("confidence", 0.0)
        needs_review = confidence < CONFIDENCE_THRESHOLD
        return {
            "id": tx["id"],
            "category": category,
            "confidence": confidence,
            "needs_review": needs_review
        }
    except Exception as e:
        print(f"Error categorizing transaction {tx['id']}: {e}")
        return None