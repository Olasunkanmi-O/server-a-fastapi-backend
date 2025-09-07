from pydantic import BaseModel
from typing import Optional

class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str
    task_type: Optional[str] = "general"
    source_model: Optional[str] = "user"
    session_id: Optional[str]

class FeedbackResponse(BaseModel):
    status: str
    message: str
    task_type: Optional[str]
    session_id: Optional[str]