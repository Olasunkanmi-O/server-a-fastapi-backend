# app/routers/categorize.py

from fastapi import APIRouter, HTTPException
from app.schemas import CategorizeResponse
from app.services.categorize_service import run_categorization_pipeline

router = APIRouter(
    prefix="/transactions",
    tags=["Categorization"]
)

@router.post("/categorize", response_model=CategorizeResponse, summary="Run transaction categorization pipeline")
async def categorize_transactions():
    """
    Categorizes new transactions using the LLM pipeline.

    Returns:
        CategorizeResponse: Structured categorization results.
    """
    try:
        result = await run_categorization_pipeline()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")