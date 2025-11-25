"""
Public endpoints (no authentication required)
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
import structlog

from app.services.ai_service import analyze_legal_query
from app.services.rag_service import retrieve_relevant_context
from app.services.ai_service import translate_text
from app.services.ocr_service import extract_text_from_image
from app.core.config import settings

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
    RAG/embeddings DISABLED for maximum speed - direct OpenAI response only
    """
    try:
        # RAG/embeddings disabled for maximum speed
        # Check config setting - if RAG is disabled, skip entirely
        rag_context = None
        
        if getattr(settings, 'ENABLE_RAG', False):
            # Only retrieve RAG context if explicitly enabled
            rag_context = await retrieve_relevant_context(
                request.query_text,
                domain=request.domain,
                location_filter=request.location,
                skip_if_offline=True
            )
        else:
            # RAG disabled - direct OpenAI response (fastest)
            rag_context = None
        
        # Build user context (minimal for public users)
        user_context = {
            "user_type": "citizen",
            "location": request.location or {},
        }
        
        # Analyze with AI directly (no RAG context for speed)
        analysis_result = await analyze_legal_query(
            query_text=request.query_text,
            domain=request.domain,
            user_context=user_context,
            language=request.language,
            rag_context=rag_context,  # None if RAG disabled
        )
        
        # Validate and normalize response
        logger.info("Analysis result received", keys=list(analysis_result.keys()))
        
        # Ensure all required fields exist with defaults
        normalized_result = {
            "analysis": analysis_result.get("analysis", "Analysis not available"),
            "risk_level": analysis_result.get("risk_level", "medium"),
            "risk_score": int(analysis_result.get("risk_score", 50)),  # Ensure int
            "risk_explanation": analysis_result.get("risk_explanation", "Risk assessment not available"),
            "pros": analysis_result.get("pros", []),
            "cons": analysis_result.get("cons", []),
            "preventive_roadmap": analysis_result.get("preventive_roadmap", []),
            "legal_references": analysis_result.get("legal_references", []),
            "warnings": analysis_result.get("warnings", []),
            "next_steps": analysis_result.get("next_steps", []),
            "lawyer_consultation_recommended": bool(analysis_result.get("lawyer_consultation_recommended", True)),
        }
        
        # Return simplified response
        return PublicQueryResponse(**normalized_result)
        
    except Exception as e:
        logger.error("Public chat failed", error=str(e), exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error("Full traceback", traceback=error_details)
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


@router.post("/ocr")
async def public_ocr(
    image: UploadFile = File(...),
    domain: str = Form("civil"),
    language: str = Form("en"),
    analyze: str = Form("true")  # Accept as string, convert to bool
):
    """
    Extract text from image using OCR and optionally analyze it
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Validate image size (max 10MB)
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
        if len(image_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image too large. Maximum size: {max_size / 1024 / 1024}MB"
            )
        
        # Extract text using OCR
        ocr_result = await extract_text_from_image(image_data, use_openai=True)
        
        result = {
            "extracted_text": ocr_result["extracted_text"],
            "document_type": ocr_result.get("document_type", "unknown"),
            "key_information": ocr_result.get("key_information", {}),
            "confidence": ocr_result.get("confidence", 0.0),
            "method_used": ocr_result.get("method_used", "unknown"),
        }
        
        # Convert analyze string to bool
        analyze_bool = analyze.lower() in ('true', '1', 'yes', 'on')
        
        # If analyze=True, also run AI analysis on extracted text
        if analyze_bool and ocr_result["extracted_text"].strip():
            try:
                # Build user context
                user_context = {
                    "user_type": "citizen",
                    "document_type": ocr_result.get("document_type", "unknown"),
                    "key_information": ocr_result.get("key_information", {}),
                }
                
                # Analyze extracted text
                analysis_result = await analyze_legal_query(
                    query_text=ocr_result["extracted_text"],
                    domain=domain,
                    user_context=user_context,
                    language=language,
                    rag_context=None,  # No RAG for speed
                )
                
                result["analysis"] = {
                    "risk_level": analysis_result.get("risk_level", "medium"),
                    "risk_score": analysis_result.get("risk_score", 50),
                    "risk_explanation": analysis_result.get("risk_explanation", ""),
                    "analysis": analysis_result.get("analysis", ""),
                    "pros": analysis_result.get("pros", []),
                    "cons": analysis_result.get("cons", []),
                    "preventive_roadmap": analysis_result.get("preventive_roadmap", []),
                    "legal_references": analysis_result.get("legal_references", []),
                    "warnings": analysis_result.get("warnings", []),
                    "next_steps": analysis_result.get("next_steps", []),
                    "lawyer_consultation_recommended": analysis_result.get("lawyer_consultation_recommended", False),
                }
            except Exception as e:
                logger.warning("AI analysis of OCR text failed", error=str(e))
                result["analysis_error"] = str(e)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("OCR processing failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )

