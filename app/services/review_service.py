# app/services/review.py

from app.db.pool import get_pool
from app.schemas import ReviewRequest, ReviewResponse
from datetime import datetime

async def process_review_submission(payload: ReviewRequest) -> ReviewResponse:
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("""
                INSERT INTO review_logs (
                    user_id, feedback, rating, timestamp, session_id
                ) VALUES ($1, $2, $3, $4, $5)
            """, payload.user_id, payload.feedback, payload.rating, datetime.utcnow(), payload.session_id)

            await conn.execute("""
                INSERT INTO conversation_logs (
                    user_id, input_text, llm_response, task_type, source_model, session_id
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, payload.user_id, payload.feedback, "Review submitted", "review", "user", payload.session_id)

    return ReviewResponse(
        status="success",
        message="Review submitted successfully.",
        rating=payload.rating,
        session_id=payload.session_id
    )