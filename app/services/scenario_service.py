# app/services/scenario_service.py

from datetime import datetime, timedelta
from app.db.pool import get_pool
from app.schemas.scenario import ScenarioRequest, ScenarioResponse
import json

# Define known categories for validation
KNOWN_CATEGORIES = {
    "sales", "income", "rent & lease", "utilities", "software",
    "marketing & advertising", "bank charges", "insurance",
    "travel & mileage", "professional development", "hmrc payments",
    "office supplies", "general expense", "uncategorized"
}

# Inline LLM call stub (replace with actual orchestration logic)
async def call_llm(prompt: str) -> dict:
    # TODO: Replace with actual LLM orchestration logic
    return {
        "response": {
            "recommendations": "Mock recommendation",
            "tax_implications": "Mock tax advice",
            "cash_flow_projection": {"month": "Mock projection"}
        },
        "confidence": 0.85,
        "source_model": "mock-llm"
    }

async def build_scenario_response(payload: ScenarioRequest) -> ScenarioResponse:
    # Extract payload fields
    user_id = payload.user_id
    user_request = payload.request
    hypothetical_changes = payload.hypothetical_changes
    session_id = payload.session_id
    scenario_type = payload.scenario_type
    timeframe_days = payload.timeframe_days
    aggregation_days = payload.aggregation_days

    pool = await get_pool()
    async with pool.acquire() as conn:
        recent_cutoff = datetime.now() - timedelta(days=timeframe_days)
        aggregation_cutoff = datetime.now() - timedelta(days=aggregation_days)

        # Fetch recent transactions
        recent_transactions = await conn.fetch("""
            SELECT date, description, amount, COALESCE(tax_category,'uncategorized') AS category
            FROM transactions
            WHERE user_id = $1 AND date >= $2
            ORDER BY date DESC
            LIMIT 20
        """, user_id, recent_cutoff)

        # Fetch aggregated transactions
        aggregated_transactions = await conn.fetch("""
            SELECT to_char(date, 'YYYY-MM') AS month, tax_category,
                   SUM(amount) AS total_amount
            FROM transactions
            WHERE user_id = $1 AND date >= $2 AND date < $3
            GROUP BY month, tax_category
            ORDER BY month DESC
            LIMIT 12
        """, user_id, aggregation_cutoff, recent_cutoff)

    # Format summaries
    recent_summary = "\n".join([
        f"- {tx['date'].strftime('%Y-%m-%d')}: {tx['description']} (£{tx['amount']}) [{tx['tax_category']}]"
        for tx in recent_transactions
    ]) if recent_transactions else "No recent transactions."

    agg_summary = "\n".join([
        f"- {row['month']} | {row['tax_category']}: £{row['total_amount']}"
        for row in aggregated_transactions
    ]) if aggregated_transactions else "No older transactions."

    # Calculate totals
    total_income = sum(tx['amount'] for tx in recent_transactions if tx['amount'] > 0)
    total_expenses = sum(-tx['amount'] for tx in recent_transactions if tx['amount'] < 0)

    # Apply hypothetical changes
    change_texts = []
    for change in hypothetical_changes:
        desc = change.get("description", "Unnamed change")
        amt = change.get("amount")
        cat = change.get("tax_category", "uncategorized").lower()

        if not isinstance(amt, (int, float)):
            raise ValueError(f"Invalid amount in hypothetical change: {desc}")
        if cat not in KNOWN_CATEGORIES:
            raise ValueError(f"Unknown category in hypothetical change: {desc}")

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

    # Construct prompt for LLM
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

    # Call LLM
    scenario_result = await call_llm(full_prompt)
    scenario_response = scenario_result.get("response", "No response from model")
    confidence_score = scenario_result.get("confidence", None)

    # Log conversation
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO conversation_logs (
                user_id, input_text, llm_response, task_type, source_model, session_id
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """, user_id, full_prompt, json.dumps(scenario_response), scenario_type, scenario_result.get("source_model", "mock-llm"), session_id)

    return ScenarioResponse(
        status="success",
        scenario=scenario_response,
        confidence=confidence_score,
        scenario_type=scenario_type
    )