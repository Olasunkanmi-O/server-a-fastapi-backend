# app/schemas/categorize.py

from pydantic import BaseModel
from typing import List, Optional

class CategorizedTransaction(BaseModel):
    id: int
    tax_category: str
    confidence: float
    needs_review: bool
    prompt: str
    response: str
    source_model: str
    user_id: Optional[str]

class CategorizeResponse(BaseModel):
    status: str
    transactions: List[CategorizedTransaction]
    low_confidence_count: int

class TransactionUpdate(BaseModel):
    id: int
    tax_category: str
    confidence: float
    needs_review: bool
    prompt: str
    response: str
    source_model: str
    user_id: Optional[str] = None