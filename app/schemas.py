# app/schemas.py
from typing import List, Optional
from pydantic import BaseModel
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


class ScenarioRequest(BaseModel):
    user_id: int
    scenario_text: str  # user's question or hypothetical

class ScenarioResponse(BaseModel):
    answer: str
    confidence: float

class ReviewResponse(BaseModel):
    status: str
    transactions: List[TransactionUpdate]

