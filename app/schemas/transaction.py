from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class Transaction(BaseModel):
    date: datetime
    amount: str
    description: str
    tax_category: Optional[str] = "Uncategorized"