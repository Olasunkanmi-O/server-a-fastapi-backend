from pydantic import BaseModel
from typing import List, Optional
from app.schemas.categorize import TransactionUpdate

class ReviewRequest(BaseModel):
    user_id: str
    feedback: str
    rating: int
    session_id: Optional[str]

class ReviewResponse(BaseModel):
    status: str
    message: str
    rating: int
    session_id: Optional[str]