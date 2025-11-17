"""
Public endpoints (no authentication required)
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import structlog

from app.services.ai_service import analyze_legal_query
from app.services.rag_service import retrieve_relevant_context
from app.services.ai_service import translate_text

logger = structlog.get_logger()
router = APIRouter()


class PublicQueryRequest(BaseModel):
    query_text: str
    domain: str = "civil"  # agriculture, civil, family, university
    language: str = "en"
    location: Optional[Dict[str, Any]] = None


class PublicQueryResponse(BaseModel):
    analysis: str
    risk_level: str
    risk_score: int
    risk_explanation: str
    pros: list
    cons: list
    preventive_roadmap: list
    legal_references: list
    warnings: list
    next_steps: list
    lawyer_consultation_recommended: bool


@router.post("/chat", response_model=PublicQueryResponse)
async def public_chat(request: PublicQueryRequest):
    """
    Public chatbot endpoint - no authentication required
    """
    try:
        # Retrieve RAG context
        rag_context = await retrieve_relevant_context(
            request.query_text,
            domain=request.domain,
            location_filter=request.location
        )
        
        # Build user context (minimal for public users)
        user_context = {
            "user_type": "citizen",
            "location": request.location or {},
        }
        
        # Analyze with AI
        analysis_result = await analyze_legal_query(
            query_text=request.query_text,
            domain=request.domain,
            user_context=user_context,
            language=request.language,
            rag_context=rag_context,
        )
        
        # Return simplified response
        return PublicQueryResponse(
            analysis=analysis_result["analysis"],
            risk_level=analysis_result["risk_level"],
            risk_score=analysis_result["risk_score"],
            risk_explanation=analysis_result["risk_explanation"],
            pros=analysis_result["pros"],
            cons=analysis_result["cons"],
            preventive_roadmap=analysis_result["preventive_roadmap"],
            legal_references=analysis_result["legal_references"],
            warnings=analysis_result["warnings"],
            next_steps=analysis_result["next_steps"],
            lawyer_consultation_recommended=analysis_result["lawyer_consultation_recommended"],
        )
        
    except Exception as e:
        logger.error("Public chat failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/translate")
async def public_translate(text: str, target_language: str, source_language: str = "en"):
    """Public translation endpoint"""
    try:
        translated = await translate_text(text, target_language, source_language)
        return {"translated_text": translated}
    except Exception as e:
        logger.error("Translation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation failed"
        )

