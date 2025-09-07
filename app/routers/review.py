# app/routers/review.py

from fastapi import APIRouter, HTTPException
from app.schemas import ReviewRequest, ReviewResponse
from app.services.review_service import process_review_submission
import logging
logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="/transactions",
    tags=["Review Logs"]
)

@router.post("/review", response_model=ReviewResponse, summary="Submit a review for a transaction or system response")
async def submit_review(payload: ReviewRequest):
    """
    Accepts a structured review payload and stores it in the review_logs table.

    Args:
        payload (ReviewRequest): Contains user ID, transaction reference, and review content.

    Returns:
        ReviewResponse: Confirmation of review submission.
    """
    try:
        result = await process_review_submission(payload)
        logger.info(f"Review submitted by user {payload.user_id} for transaction {payload.transaction_id}")
        return result
    except Exception as e:
        logger.error(f"Review submission failed for user {payload.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Review submission failed: {str(e)}")


@router.get("/review/health")
async def review_health():
    return {"status": "review router active"}