# app/routers/feedback.py

from fastapi import APIRouter, HTTPException
from app.schemas import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import submit_feedback

router = APIRouter(
    prefix="/user",
    tags=["User Feedback"]
)

@router.post("/feedback", response_model=FeedbackResponse, summary="Submit feedback on system response or experience")
async def receive_feedback(payload: FeedbackRequest):
    """
    Accepts structured user feedback and stores it in the feedback_logs table.

    Args:
        payload (FeedbackRequest): Contains user ID, feedback text, and optional metadata.

    Returns:
        FeedbackResponse: Confirmation of feedback submission.
    """
    try:
        result = await submit_feedback(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "feedback router active"}