from app.db.pool import get_pool
from app.schemas import FeedbackRequest, FeedbackResponse
from datetime import datetime

async def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("""
                INSERT INTO feedback_logs (
                    user_id, feedback, task_type, source_model, session_id, timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, payload.user_id, payload.feedback, payload.task_type, payload.source_model, payload.session_id, datetime.utcnow())

            await conn.execute("""
                INSERT INTO conversation_logs (
                    user_id, input_text, llm_response, task_type, source_model, session_id
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, payload.user_id, payload.feedback, "Feedback received", payload.task_type, payload.source_model, payload.session_id)

    return FeedbackResponse(
        status="success",
        message="Feedback recorded.",
        task_type=payload.task_type,
        session_id=payload.session_id
    )