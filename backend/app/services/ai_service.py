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
client = OpenAI(api_key=settings.OPENAI_API_KEY)


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
    rag_context: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Analyze a legal query using GPT-4o with RAG context
    
    Args:
        query_text: User's legal question
        domain: Legal domain (agriculture, civil, family, university)
        user_context: User information (type, location, etc.)
        language: Preferred language for response
        rag_context: Retrieved context from RAG pipeline
        
    Returns:
        Structured legal analysis
    """
    start_time = time.time()
    
    try:
        # Build system prompt
        system_prompt = build_system_prompt(domain, user_context, language)
        
        # Build user prompt with RAG context
        user_prompt = build_user_prompt(query_text, rag_context, language)
        
        # Call OpenAI with function calling
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            functions=[LEGAL_ANALYSIS_FUNCTION],
            function_call={"name": "analyze_legal_query"},
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )
        
        # Extract function call result
        function_call = response.choices[0].message.function_call
        if function_call and function_call.name == "analyze_legal_query":
            result = json.loads(function_call.arguments)
            
            processing_time = int((time.time() - start_time) * 1000)
            tokens_used = response.usage.total_tokens if response.usage else None
            
            result.update({
                "model_version": settings.OPENAI_MODEL,
                "processing_time_ms": processing_time,
                "tokens_used": tokens_used,
            })
            
            logger.info(
                "Legal query analyzed",
                domain=domain,
                processing_time_ms=processing_time,
                tokens_used=tokens_used,
            )
            
            return result
        else:
            raise ValueError("No function call in response")
            
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
    """Build user prompt with RAG context"""
    prompt = f"Legal Query: {query_text}\n\n"
    
    if rag_context:
        prompt += "Relevant Legal Context:\n"
        for i, context in enumerate(rag_context[:5], 1):  # Top 5 chunks
            prompt += f"\n[{i}] {context.get('text', '')}\n"
            if context.get('metadata'):
                prompt += f"Source: {context['metadata'].get('source', 'Unknown')}\n"
    
    prompt += "\nPlease provide a comprehensive legal analysis with risk assessment, preventive roadmap, and legal references."
    
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


async def transcribe_audio(audio_file_path: str, language_hint: str = "hi") -> Dict[str, Any]:
    """Transcribe audio using OpenAI Whisper"""
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
        logger.error("Transcription failed", error=str(e))
        raise


async def synthesize_speech(text: str, voice: str = "alloy", language: str = "en") -> bytes:
    """Convert text to speech using OpenAI TTS"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        return response.content
    except Exception as e:
        logger.error("Speech synthesis failed", error=str(e))
        raise

