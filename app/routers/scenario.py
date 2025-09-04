from fastapi import APIRouter, HTTPException
from app.db.pool import get_pool
from app.providers.factory import get_provider
from app.config import settings
from app.schemas import ScenarioRequest, ScenarioResponse

router = APIRouter()
provider = get_provider(settings.LLM_PROVIDER)

@router.post("/scenario", response_model=ScenarioResponse)
async def run_scenario(request: ScenarioRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        transactions = await conn.fetch("""
            SELECT date, description, amount, category, needs_review
            FROM transactions
            WHERE user_id = $1
        """, request.user_id)

    transaction_list = [
        {
            "date": str(tx["date"]),
            "description": tx["description"],
            "amount": float(tx["amount"]),
            "category": tx["category"],
            "needs_review": tx["needs_review"]
        }
        for tx in transactions
    ]

    try:
        # ✅ Use the correct method from your Gemini provider
        response_text = provider.summarize_business_health(
            query=request.scenario_text,
            transactions=transaction_list
        )

        return ScenarioResponse(
            answer=response_text,
            confidence=1.0  # You can later parse confidence if Gemini returns structured output
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")