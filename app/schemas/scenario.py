# app/schemas/scenario.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.schemas.transaction import Transaction  
#from app.schemas.hypothetical_change import HypotheticalChange 

class HypotheticalChange(BaseModel):
    description: str
    amount: float
    tax_category: Optional[str] = "Uncategorized"


class ScenarioRequest(BaseModel):
    user_id: int
    query: str
    request: List[Transaction]
    session_id: Optional[str]
    scenario_type: str
    timeframe_days: int
    aggregation_days: int
    hypothetical_changes: List[str]

class CashFlowProjection(BaseModel):
    initial_impact: Optional[str]
    estimated_tax_savings: Optional[str]
    net_effect: Optional[str]

class Scenario(BaseModel):
    recommendations: str
    tax_implications: str
    cash_flow_projection: CashFlowProjection

class ScenarioResponse(BaseModel):
    status: str
    scenario_type: str
    scenario: Dict[str, Any]
    confidence: Optional[float]
    cash_flow_projection: Optional[Dict[str, Any]] = None

