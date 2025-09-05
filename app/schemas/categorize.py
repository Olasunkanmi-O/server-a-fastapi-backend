from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class TransactionUpdate(BaseModel):
    id: int
    description: str
    amount: float
    date: Optional[date] = None
    category: str = "Uncategorized"
    needs_review: bool = True
    confidence: float = 0.0

class CategorizeResponse(BaseModel):
    status: str
    transactions: List[TransactionUpdate] = []
    low_confidence_count: int