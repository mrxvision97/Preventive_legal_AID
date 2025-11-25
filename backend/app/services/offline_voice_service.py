"""
Offline voice service for edge devices
Supports local Whisper for transcription and local TTS
"""
from typing import Dict, Any, Optional
import structlog
import os
import subprocess
import tempfile

logger = structlog.get_logger()

# Try importing local Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

# Try importing pyttsx3 for offline TTS
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None


async def transcribe_audio_offline(
    audio_file_path: str,
    language_hint: str = "hi",
    model_size: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribe audio using local Whisper model (offline)
    Optimized for edge devices like Jetson Nano
    
    Args:
        audio_file_path: Path to audio file
        language_hint: Language code (hi, en, ta, te, bn, mr)
        model_size: Whisper model size (tiny, base, small, medium, large)
                   Auto-selected for edge devices if None
    
    Returns:
        Transcription result with text and language
    """
    if not WHISPER_AVAILABLE:
        raise Exception("Whisper not installed. Install with: pip install openai-whisper")
    
    try:
        # Auto-detect optimal model size for edge devices
        if model_size is None:
            from app.core.edge_optimization import get_optimal_whisper_model
            model_size = get_optimal_whisper_model()
            logger.info("Auto-selected Whisper model", model_size=model_size, reason="edge optimization")
        
        # Load model (cached after first load, runs in thread pool for async)
        logger.info("Loading Whisper model", model_size=model_size)
        loop = asyncio.get_event_loop()
        model = await loop.run_in_executor(None, whisper.load_model, model_size)
        
        # Map language hints to Whisper language codes
        language_map = {
            "hi": "hi",
            "en": "en",
            "ta": "ta",
            "te": "te",
            "bn": "bn",
            "mr": "mr"
        }
        whisper_lang = language_map.get(language_hint, None)
        
        # Transcribe (run in thread pool for async)
        logger.info("Transcribing audio", file=audio_file_path, language=whisper_lang)
        result = await loop.run_in_executor(
            None,
            model.transcribe,
            audio_file_path,
            whisper_lang,
            "transcribe"
        )
        
        return {
            "text": result["text"].strip(),
            "language": result.get("language", language_hint),
            "confidence": 1.0,  # Whisper doesn't provide confidence scores
        }
        
    except Exception as e:
        logger.error("Offline transcription failed", error=str(e))
        raise


async def synthesize_speech_offline(
    text: str,
    language: str = "en",
    voice: str = "default"
) -> bytes:
    """
    Synthesize speech using offline TTS (pyttsx3)
    Optimized for edge devices
    
    Args:
        text: Text to convert to speech
        language: Language code
        voice: Voice identifier
    
    Returns:
        Audio bytes (WAV format)
    """
    if not PYTTSX3_AVAILABLE:
        raise Exception("pyttsx3 not installed. Install with: pip install pyttsx3")
    
    try:
        # Run TTS in thread pool for async
        loop = asyncio.get_event_loop()
        
        def _synthesize():
            engine = pyttsx3.init()
            
            # Configure voice settings
            voices = engine.getProperty('voices')
            
            # Try to set language-appropriate voice
            if language == "hi" and len(voices) > 1:
                # Try to find Hindi voice (if available)
                for v in voices:
                    if "hindi" in v.name.lower() or "hi" in v.id.lower():
                        engine.setProperty('voice', v.id)
                        break
            
            # Set speech rate and volume (optimized for edge)
            engine.setProperty('rate', 150)  # Speed
            engine.setProperty('volume', 0.9)  # Volume
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                engine.save_to_file(text, tmp_path)
                engine.runAndWait()
                
                # Read audio file
                with open(tmp_path, 'rb') as f:
                    audio_bytes = f.read()
                
                return audio_bytes, tmp_path
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise
        
        audio_bytes, tmp_path = await loop.run_in_executor(None, _synthesize)
        
        # Clean up
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except:
            pass
        
        return audio_bytes
                
    except Exception as e:
        logger.error("Offline TTS failed", error=str(e))
        raise


def check_whisper_available() -> bool:
    """Check if local Whisper is available"""
    return WHISPER_AVAILABLE


def check_tts_available() -> bool:
    """Check if offline TTS is available"""
    return PYTTSX3_AVAILABLE


async def get_voice_service_status() -> Dict[str, bool]:
    """Get status of voice services"""
    return {
        "whisper_available": check_whisper_available(),
        "tts_available": check_tts_available(),
        "online_whisper": True,  # OpenAI Whisper API
        "online_tts": True,  # OpenAI TTS API
    }

