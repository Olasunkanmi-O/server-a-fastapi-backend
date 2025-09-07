# app/routers/scenario.py

from fastapi import APIRouter, HTTPException
from app.schemas.scenario import ScenarioRequest, ScenarioResponse
from app.services.scenario_service import build_scenario_response

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/transactions",
    tags=["Scenario Simulation"]
)

@router.post("/scenario", response_model=ScenarioResponse, summary="Generate financial scenario based on user input")
async def generate_financial_scenario(payload: ScenarioRequest):
    """
    Generates a financial scenario using user-provided context and LLM inference.

    Args:
        payload (ScenarioRequest): Contains user ID and scenario prompt.

    Returns:
        ScenarioResponse: Structured recommendations, projections, and metadata.
    """
    if not payload.user_id or not payload.request:
        raise HTTPException(status_code=400, detail="Missing user_id or request")

    try:
        response = await build_scenario_response(payload)
        return response
    except Exception as e:
        logger.error(f"Scenario generation failed for user {payload.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Scenario generation failed")