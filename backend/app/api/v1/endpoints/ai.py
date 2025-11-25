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

# DB/Auth imports commented out - running without DB
# from app.api.v1.endpoints.auth import get_current_user
# from app.models.user import User

import structlog

logger = structlog.get_logger()
router = APIRouter()


class AnalyzeRequest(BaseModel):
    query_text: str
    domain: str
    user_context: Optional[Dict[str, Any]] = None
    language: str = "en"


# DB-dependent endpoints commented out - use /public/chat instead
# @router.post("/analyze")
# async def analyze_query(
#     request: AnalyzeRequest,
#     current_user: User = Depends(get_current_user),
# ):
#     """Direct AI analysis endpoint for testing"""
#     Use /public/chat endpoint instead - no authentication required


class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "en"


# Use /public/translate endpoint instead - no authentication required
# @router.post("/translate")
# async def translate(
#     request: TranslateRequest,
#     current_user: User = Depends(get_current_user),
# ):
#     """Translate text between supported languages"""
#     Use /public/translate endpoint instead


@router.post("/transcribe")
async def transcribe(
    audio_file: UploadFile = File(...),
    language_hint: str = "hi",
    use_offline: bool = False,
    # current_user removed - public endpoint (no DB required)
):
    """
    Transcribe audio file to text
    Supports both online (OpenAI Whisper) and offline (local Whisper) modes
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            result = await transcribe_audio(tmp_path, language_hint, use_offline=use_offline)
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
    use_offline: bool = False,
    # current_user removed - public endpoint (no DB required)
):
    """
    Convert text to speech
    Supports both online (OpenAI TTS) and offline (pyttsx3) modes
    """
    try:
        audio_bytes = await synthesize_speech(
            text=request.text,
            voice=request.voice,
            language=request.language,
            use_offline=use_offline,
        )
        
        from fastapi.responses import Response
        # Determine content type based on offline/online
        content_type = "audio/wav" if use_offline else "audio/mpeg"
        filename = "speech.wav" if use_offline else "speech.mp3"
        
        return Response(
            content=audio_bytes,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error("Speech synthesis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.get("/suggestions")
async def get_suggestions(
    # current_user removed - public endpoint (no DB required)
):
    """Get topic suggestions (public endpoint)"""
    suggestions = [
        "Agricultural land leasing rights",
        "Tenant protection laws",
        "Crop insurance claims",
        "Water rights for farmers",
        "Minimum support price policies",
    ]
    
    return {"suggestions": suggestions}

