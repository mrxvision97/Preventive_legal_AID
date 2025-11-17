"""
AI processing endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
import tempfile
import os

from app.services.ai_service import (
    analyze_legal_query,
    translate_text,
    transcribe_audio,
    synthesize_speech,
)
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
import structlog

logger = structlog.get_logger()
router = APIRouter()


class AnalyzeRequest(BaseModel):
    query_text: str
    domain: str
    user_context: Optional[Dict[str, Any]] = None
    language: str = "en"


@router.post("/analyze")
async def analyze_query(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """Direct AI analysis endpoint for testing"""
    try:
        user_context = request.user_context or {
            "user_type": current_user.user_type.value,
            "location": current_user.location or {},
        }
        
        result = await analyze_legal_query(
            query_text=request.query_text,
            domain=request.domain,
            user_context=user_context,
            language=request.language,
        )
        
        return result
    except Exception as e:
        logger.error("AI analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "en"


@router.post("/translate")
async def translate(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
):
    """Translate text between supported languages"""
    try:
        translated = await translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
        )
        return {"translated_text": translated}
    except Exception as e:
        logger.error("Translation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/transcribe")
async def transcribe(
    audio_file: UploadFile = File(...),
    language_hint: str = "hi",
    current_user: User = Depends(get_current_user),
):
    """Transcribe audio file to text"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            result = await transcribe_audio(tmp_path, language_hint)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error("Transcription failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "alloy"
    language: str = "en"


@router.post("/synthesize")
async def synthesize(
    request: SynthesizeRequest,
    current_user: User = Depends(get_current_user),
):
    """Convert text to speech"""
    try:
        audio_bytes = await synthesize_speech(
            text=request.text,
            voice=request.voice,
            language=request.language,
        )
        
        from fastapi.responses import Response
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        logger.error("Speech synthesis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.get("/suggestions")
async def get_suggestions(
    current_user: User = Depends(get_current_user),
):
    """Get personalized topic suggestions"""
    # TODO: Implement personalized suggestions based on user history
    suggestions = [
        "Agricultural land leasing rights",
        "Tenant protection laws",
        "Crop insurance claims",
        "Water rights for farmers",
        "Minimum support price policies",
    ]
    
    return {"suggestions": suggestions}

