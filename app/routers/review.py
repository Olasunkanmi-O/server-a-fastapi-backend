# app/routers/review.py

from fastapi import APIRouter, HTTPException
from app.schemas import ReviewRequest, ReviewResponse
from app.services.review_service import process_review_submission

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
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review submission failed: {str(e)}")