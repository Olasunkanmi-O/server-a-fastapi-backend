from fastapi import APIRouter, Request, HTTPException
from app.db.pool import get_pool
from app.schemas.scenario import ScenarioRequest, ScenarioResponse
from app.services.scenario import generate_scenario
from datetime import datetime, timedelta


router = APIRouter()

KNOWN_CATEGORIES = {
    "food", "travel", "office supplies", "marketing", "utilities",
    "salary", "equipment", "software", "uncategorized", "other"
}

@router.post("/scenario", response_model=ScenarioResponse)
async def generate_financial_scenario(payload: ScenarioRequest):   
    user_id = payload.user_id
    user_request = payload.request
    hypothetical_changes = payload.hypothetical_changes
    session_id = payload.session_id
    scenario_type = payload.scenario_type
    timeframe_days = payload.timeframe_days
    aggregation_days = payload.aggregation_days

    if not user_id or not user_request:
        raise HTTPException(status_code=400, detail="Missing user_id or request")

    pool = await get_pool()
    async with pool.acquire() as conn:
        recent_cutoff = datetime.now() - timedelta(days=timeframe_days)
        aggregation_cutoff = datetime.now() - timedelta(days=aggregation_days)

        recent_transactions = await conn.fetch("""
            SELECT date, description, amount, COALESCE(category,'uncategorized') AS category
            FROM transactions
            WHERE user_id = $1 AND date >= $2
            ORDER BY date DESC
            LIMIT 20
        """, user_id, recent_cutoff)

        aggregated_transactions = await conn.fetch("""
            SELECT to_char(date, 'YYYY-MM') AS month, category, 
                   SUM(amount) AS total_amount
            FROM transactions
            WHERE user_id = $1 AND date >= $2 AND date < $3
            GROUP BY month, category
            ORDER BY month DESC
            LIMIT 12
        """, user_id, aggregation_cutoff, recent_cutoff)

    recent_summary = "\n".join([
        f"- {tx['date'].strftime('%Y-%m-%d')}: {tx['description']} (£{tx['amount']}) [{tx['category']}]"
        for tx in recent_transactions
    ]) if recent_transactions else "No recent transactions."

    agg_summary = "\n".join([
        f"- {row['month']} | {row['category']}: £{row['total_amount']}"
        for row in aggregated_transactions
    ]) if aggregated_transactions else "No older transactions."

    total_income = sum(tx['amount'] for tx in recent_transactions if tx['amount'] > 0)
    total_expenses = sum(-tx['amount'] for tx in recent_transactions if tx['amount'] < 0)
    change_texts = []

    for change in hypothetical_changes:
        desc = change.get("description", "Unnamed change")
        amt = change.get("amount")
        cat = change.get("category", "uncategorized").lower()

        if not isinstance(amt, (int, float)):
            raise HTTPException(status_code=400, detail=f"Invalid amount in hypothetical change: {desc}")
        if cat not in KNOWN_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Unknown category in hypothetical change: {desc}")

        if amt > 0:
            total_income += amt
        else:
            total_expenses += -amt

        change_texts.append(f"- {desc} (£{amt}) [{cat}]")

    hypothetical_summary = "\n".join(change_texts) if change_texts else "No hypothetical changes."
    net_balance = total_income - total_expenses

    summary_text = (
        f"Total income over last {timeframe_days} days + hypothetical changes: £{total_income}\n"
        f"Total expenses over last {timeframe_days} days + hypothetical changes: £{total_expenses}\n"
        f"Net balance over this period: £{net_balance}\n"
    )

    full_prompt = (
        f"User request: {user_request}\n\n"
        f"Recent transactions (detailed):\n{recent_summary}\n\n"
        f"Older transactions (aggregated by month/category):\n{agg_summary}\n\n"
        f"Hypothetical changes:\n{hypothetical_summary}\n\n"
        f"Summary:\n{summary_text}\n\n"
        "Instructions:\n"
        "- Provide scenario analysis based on actual transactions and hypothetical changes.\n"
        "- Highlight potential tax implications.\n"
        "- Suggest strategies for cash flow, savings, or expense management.\n"
        "- Simulate the impact of any proposed changes the user mentions.\n"
        "- Return your response in JSON format with keys: 'recommendations', 'tax_implications', 'cash_flow_projection'."
    )

    try:
        scenario_result = await generate_scenario(full_prompt)
        scenario_response = scenario_result.get("response", "No response from model")
        confidence_score = scenario_result.get("confidence", None)
    except Exception as e:
        scenario_response = f"Error generating scenario: {str(e)}"
        confidence_score = None

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO conversation_logs (
                user_id, input_text, llm_response, task_type, source_model, session_id
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """, user_id, full_prompt, scenario_response, scenario_type, scenario_result.get("source_model"), session_id)

    return ScenarioResponse(
        status="success",
        scenario=scenario_response,
        confidence=confidence_score,
        scenario_type=scenario_type
    )