"""
AI Service for legal analysis using OpenAI GPT-4o
"""
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.core.config import settings
import structlog
import json
import time

logger = structlog.get_logger()

# Initialize OpenAI client only if API key is available
client = None

# Check if API key is set (including from .env)
if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY.strip())
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.warning("Failed to initialize OpenAI client", error=str(e))
else:
    logger.warning("OpenAI API key not set. Please set OPENAI_API_KEY in .env file")


# Function calling schema for structured output
LEGAL_ANALYSIS_FUNCTION = {
    "name": "analyze_legal_query",
    "description": "Analyze a legal query and provide comprehensive preventive legal guidance",
    "parameters": {
        "type": "object",
        "properties": {
            "risk_level": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Overall risk level of the legal situation"
            },
            "risk_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Risk score from 0 (no risk) to 100 (critical risk)"
            },
            "risk_explanation": {
                "type": "string",
                "description": "Detailed explanation of the risk assessment"
            },
            "analysis": {
                "type": "string",
                "description": "Comprehensive legal analysis in simple, understandable language"
            },
            "pros": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of advantages or positive aspects"
            },
            "cons": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of disadvantages or negative aspects"
            },
            "preventive_roadmap": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step_number": {"type": "integer"},
                        "action": {"type": "string"},
                        "importance": {"type": "string"},
                        "deadline": {"type": "string", "nullable": True},
                        "resources_needed": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["step_number", "action", "importance"]
                },
                "description": "Step-by-step preventive action plan"
            },
            "legal_references": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "act_name": {"type": "string"},
                        "section_number": {"type": "string"},
                        "summary": {"type": "string"},
                        "relevance": {"type": "string"}
                    },
                    "required": ["act_name", "summary", "relevance"]
                },
                "description": "Relevant legal acts and sections"
            },
            "warnings": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Important warnings and red flags"
            },
            "lawyer_consultation_recommended": {
                "type": "boolean",
                "description": "Whether professional lawyer consultation is recommended"
            },
            "next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Immediate next steps the user should take"
            }
        },
        "required": [
            "risk_level", "risk_score", "risk_explanation", "analysis",
            "pros", "cons", "preventive_roadmap", "legal_references",
            "warnings", "lawyer_consultation_recommended", "next_steps"
        ]
    }
}


async def analyze_legal_query(
    query_text: str,
    domain: str,
    user_context: Optional[Dict[str, Any]] = None,
    language: str = "en",
    rag_context: Optional[List[Dict[str, Any]]] = None,
    use_fallback: bool = True
) -> Dict[str, Any]:
    """
    Analyze a legal query using GPT-4o with RAG context
    
    Args:
        query_text: User's legal question
        domain: Legal domain (agriculture, civil, family, university)
        user_context: User information (type, location, etc.)
        language: Preferred language for response
        rag_context: Retrieved context from RAG pipeline
        use_fallback: If True, fallback to Ollama if OpenAI fails
        
    Returns:
        Structured legal analysis
    """
    # Use fallback system if enabled
    if use_fallback:
        try:
            # Check if we should prefer online models (default: True on laptops, False on edge)
            from app.core.edge_optimization import is_edge_device
            from app.core.config import settings
            prefer_online = not is_edge_device() and not settings.USE_OFFLINE_MODE
            
            from app.services.model_service import analyze_legal_query_with_fallback
            return await analyze_legal_query_with_fallback(
                query_text, domain, user_context, language, rag_context, prefer_online=prefer_online
            )
        except Exception as e:
            logger.warning("Fallback system failed", error=str(e))
            # If fallback fails and we're in offline mode, raise the error
            if settings.USE_OFFLINE_MODE:
                raise Exception(f"Offline mode enabled but Ollama is not available: {str(e)}")
            # Otherwise, try OpenAI if available
            if not client:
                raise Exception("No AI service available. Check OpenAI API key or start Ollama.")
    
    # If we reach here, fallback was disabled or failed, try OpenAI directly
    if not client:
        raise Exception("OpenAI client not initialized. Set OPENAI_API_KEY or enable offline mode with Ollama.")
    
    start_time = time.time()
    
    try:
        # Build system prompt
        system_prompt = build_system_prompt(domain, user_context, language)
        
        # Build user prompt with RAG context
        user_prompt = build_user_prompt(query_text, rag_context, language)
        
        # Use JSON mode instead of function calling (avoids Pydantic BaseModel issues)
        # This is simpler and faster, avoiding the Pydantic compatibility problem
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')  # Default to faster model
        max_tokens = min(getattr(settings, 'OPENAI_MAX_TOKENS', 2000), 2000)  # Limit to 2000 for speed
        temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.3)  # Lower temp = faster + more consistent
        
        # Add JSON schema instruction to system prompt
        json_schema_instruction = "\n\nIMPORTANT: Respond with valid JSON only in this exact format:\n"
        json_schema_instruction += json.dumps({
            "risk_level": "low",
            "risk_score": 0,
            "risk_explanation": "string",
            "analysis": "string",
            "pros": ["string"],
            "cons": ["string"],
            "preventive_roadmap": [{"step_number": 1, "action": "string", "importance": "string"}],
            "legal_references": [{"act_name": "string", "section_number": "string", "summary": "string", "relevance": "string"}],
            "warnings": ["string"],
            "lawyer_consultation_recommended": False,
            "next_steps": ["string"]
        }, indent=2)
        
        enhanced_system_prompt = system_prompt + json_schema_instruction
        enhanced_user_prompt = user_prompt + "\n\nReturn ONLY valid JSON, no other text."
        
        # Use JSON mode (simpler, avoids Pydantic issues)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": enhanced_user_prompt}
            ],
            response_format={"type": "json_object"},  # JSON mode - avoids Pydantic BaseModel issues
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30.0,  # 30 second timeout for faster failure
        )
        
        # Extract JSON from content (simpler than function calling)
        message = response.choices[0].message
        if message.content:
            try:
                result = json.loads(message.content)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON response", error=str(e), content=message.content[:200])
                # Fallback: create basic structure
                result = {
                    "analysis": message.content,
                    "risk_level": "medium",
                    "risk_score": 50,
                    "risk_explanation": "Analysis provided but JSON parsing failed",
                    "pros": [],
                    "cons": [],
                    "preventive_roadmap": [],
                    "legal_references": [],
                    "warnings": [],
                    "next_steps": [],
                    "lawyer_consultation_recommended": False
                }
        else:
            raise ValueError("No content in response")
        
        # Add metadata to result
        processing_time = int((time.time() - start_time) * 1000)
        tokens_used = response.usage.total_tokens if response.usage else None
        
        result.update({
            "model_version": model,
            "processing_time_ms": processing_time,
            "tokens_used": tokens_used,
        })
        
        # Reduced logging for speed - only log if processing time is high
        if processing_time > 5000:  # Only log if > 5 seconds
            logger.info(
                "Legal query analyzed",
                domain=domain,
                processing_time_ms=processing_time,
                tokens_used=tokens_used,
            )
        
        return result
            
    except Exception as e:
        logger.error("AI analysis failed", error=str(e), domain=domain)
        raise


def build_system_prompt(domain: str, user_context: Optional[Dict[str, Any]], language: str) -> str:
    """Build system prompt for legal analysis"""
    user_type = user_context.get("user_type", "citizen") if user_context else "citizen"
    location = user_context.get("location", {}) if user_context else {}
    
    prompt = f"""You are an expert legal advisor specializing in {domain} law in India. 
Your role is to provide preventive legal guidance to help users understand legal issues BEFORE they escalate into conflicts.

User Context:
- User Type: {user_type}
- Location: {location.get('city', 'N/A')}, {location.get('state', 'N/A')}

Your responses must:
1. Be clear, simple, and accessible to non-legal professionals
2. Focus on PREVENTION rather than litigation
3. Provide actionable steps users can take immediately
4. Include relevant Indian legal acts and sections
5. Assess risk levels accurately
6. Recommend professional consultation when necessary
7. Be culturally sensitive and appropriate for rural and urban Indian contexts

Always prioritize user safety and legal compliance."""
    
    return prompt


def build_user_prompt(query_text: str, rag_context: Optional[List[Dict[str, Any]]], language: str) -> str:
    """Build user prompt - RAG context skipped for speed"""
    # Skip RAG context entirely for maximum speed
    # Direct query to OpenAI without vector database lookup
    prompt = f"Legal Query: {query_text}\n\n"
    prompt += "Provide concise legal analysis with risk assessment, preventive roadmap, and key legal references for Indian law."
    
    # RAG context is intentionally skipped for speed
    # If you need RAG, set ENABLE_RAG=true in config
    
    return prompt


async def translate_text(text: str, target_language: str, source_language: str = "en") -> str:
    """Translate text using GPT-4"""
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator specializing in legal terminology. Translate accurately while preserving legal terms and context."
                },
                {
                    "role": "user",
                    "content": f"Translate the following text from {source_language} to {target_language}. Preserve legal terminology and maintain accuracy:\n\n{text}"
                }
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error("Translation failed", error=str(e))
        return text  # Return original if translation fails


async def transcribe_audio(audio_file_path: str, language_hint: str = "hi", use_offline: bool = False) -> Dict[str, Any]:
    """
    Transcribe audio using OpenAI Whisper or local Whisper
    
    Args:
        audio_file_path: Path to audio file
        language_hint: Language code
        use_offline: If True, use local Whisper even if online
    
    Returns:
        Transcription result
    """
    # Try offline first if requested or if OpenAI is unavailable
    if use_offline:
        try:
            from app.services.offline_voice_service import transcribe_audio_offline
            logger.info("Using offline Whisper for transcription")
            return await transcribe_audio_offline(audio_file_path, language_hint, model_size="base")
        except Exception as e:
            logger.warning("Offline transcription failed, trying online", error=str(e))
    
    # Try OpenAI Whisper (online)
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language_hint if language_hint != "en" else None,
            )
        
        return {
            "text": transcript.text,
            "language": transcript.language,
            "duration": getattr(transcript, "duration", None),
        }
    except Exception as e:
        logger.warning("Online transcription failed, trying offline", error=str(e))
        # Fallback to offline
        try:
            from app.services.offline_voice_service import transcribe_audio_offline
            logger.info("Falling back to offline Whisper")
            return await transcribe_audio_offline(audio_file_path, language_hint, model_size="base")
        except Exception as offline_error:
            logger.error("All transcription methods failed", error=str(offline_error))
            raise Exception(f"Transcription failed: {str(e)}")


async def synthesize_speech(text: str, voice: str = "alloy", language: str = "en", use_offline: bool = False) -> bytes:
    """
    Convert text to speech using OpenAI TTS or offline TTS
    
    Args:
        text: Text to convert
        voice: Voice identifier
        language: Language code
        use_offline: If True, use local TTS even if online
    
    Returns:
        Audio bytes
    """
    # Try offline first if requested
    if use_offline:
        try:
            from app.services.offline_voice_service import synthesize_speech_offline
            logger.info("Using offline TTS")
            return await synthesize_speech_offline(text, language, voice)
        except Exception as e:
            logger.warning("Offline TTS failed, trying online", error=str(e))
    
    # Try OpenAI TTS (online)
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        return response.content
    except Exception as e:
        logger.warning("Online TTS failed, trying offline", error=str(e))
        # Fallback to offline
        try:
            from app.services.offline_voice_service import synthesize_speech_offline
            logger.info("Falling back to offline TTS")
            return await synthesize_speech_offline(text, language, voice)
        except Exception as offline_error:
            logger.error("All TTS methods failed", error=str(offline_error))
            raise Exception(f"Speech synthesis failed: {str(e)}")

