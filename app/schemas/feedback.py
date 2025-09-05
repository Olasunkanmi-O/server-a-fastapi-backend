from pydantic import BaseModel
from typing import Optional

class FeedbackRequest(BaseModel):
    user_id: int
    conversation_id: int
    feedback_text: str
    rating: Optional[int] = None  # 1–5 scale or binary

class FeedbackResponse(BaseModel):
    status: str
    message: Optional[str] = None