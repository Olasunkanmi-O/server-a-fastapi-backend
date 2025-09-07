# app/schemas/scenario.py

from pydantic import BaseModel
from typing import List, Optional

class HypotheticalChange(BaseModel):
    description: str
    amount: float
    category: str

class ScenarioRequest(BaseModel):
    user_id: str
    request: str
    session_id: Optional[str]
    scenario_type: str
    timeframe_days: int
    aggregation_days: int
    hypothetical_changes: List[HypotheticalChange]

class CashFlowProjection(BaseModel):
    initial_impact: float
    estimated_tax_savings: Optional[float]
    net_effect: Optional[float]

class Scenario(BaseModel):
    recommendations: str
    tax_implications: str
    cash_flow_projection: CashFlowProjection

class ScenarioResponse(BaseModel):
    status: str
    scenario: Scenario
    confidence: Optional[float]
    scenario_type: str