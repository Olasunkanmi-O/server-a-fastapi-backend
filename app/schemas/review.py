from pydantic import BaseModel
from typing import List
from app.schemas.categorize import TransactionUpdate

class ReviewResponse(BaseModel):
    status: str
    transactions: List[TransactionUpdate]