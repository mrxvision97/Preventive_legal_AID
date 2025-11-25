"""
Model Service with offline/online fallback
Supports OpenAI (online) and Ollama (offline) models
"""
from typing import Dict, Any, Optional, List
from app.core.config import settings
import structlog
import httpx
import asyncio
import json

logger = structlog.get_logger()

# Try importing OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# Ollama configuration (from settings)
OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL
OLLAMA_MODEL = settings.OLLAMA_MODEL


async def check_openai_connection() -> bool:
    """Check if OpenAI API is accessible - SKIPPED for speed (just verify API key exists)"""
    # Skip actual connection check for maximum speed
    # Just verify API key exists - saves 1-2 seconds per request
    if not OPENAI_AVAILABLE or not settings.OPENAI_API_KEY:
        return False
    
    # Return True immediately if API key exists (assume it works)
    # This eliminates the 1-2 second connection check delay
    return True


async def check_ollama_connection() -> bool:
    """Check if Ollama is running locally (quick check)"""
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:  # Faster timeout
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return response.status_code == 200
    except Exception:
        return False


async def get_available_model() -> str:
    """
    Determine which model to use based on connectivity
    Returns: 'openai' or 'ollama'
    """
    # Check OpenAI first (preferred)
    if await check_openai_connection():
        logger.info("Using OpenAI model (online)")
        return "openai"
    
    # Fallback to Ollama
    if await check_ollama_connection():
        logger.info("Using Ollama model (offline)")
        return "ollama"
    
    # No models available
    raise Exception("No AI models available. Check OpenAI API key or start Ollama locally.")


async def analyze_with_openai(
    query_text: str,
    domain: str,
    user_context: Optional[Dict[str, Any]],
    language: str,
    rag_context: Optional[List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """Analyze using OpenAI GPT-4o - DIRECT call to avoid recursion"""
    # Call OpenAI directly to avoid circular dependency with analyze_legal_query
    from app.services.ai_service import client, build_system_prompt, build_user_prompt
    from app.core.config import settings
    import json
    import time
    
    if not client:
        raise Exception("OpenAI client not initialized. Set OPENAI_API_KEY in .env file")
    
    start_time = time.time()
    
    try:
        # Build prompts
        system_prompt = build_system_prompt(domain, user_context, language)
        user_prompt = build_user_prompt(query_text, rag_context, language)
        
        # Add JSON schema instruction
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
        
        # Get model settings
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        max_tokens = min(getattr(settings, 'OPENAI_MAX_TOKENS', 2000), 2000)
        temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.3)
        
        # Call OpenAI directly
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": enhanced_user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30.0,
        )
        
        # Parse response
        message = response.choices[0].message
        if message.content:
            try:
                result = json.loads(message.content)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON response", error=str(e))
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
        
        # Add metadata
        processing_time = int((time.time() - start_time) * 1000)
        tokens_used = response.usage.total_tokens if response.usage else None
        
        result.update({
            "model_version": model,
            "processing_time_ms": processing_time,
            "tokens_used": tokens_used,
        })
        
        return result
        
    except Exception as e:
        logger.error("OpenAI analysis failed", error=str(e))
        raise


async def analyze_with_ollama(
    query_text: str,
    domain: str,
    user_context: Optional[Dict[str, Any]],
    language: str,
    rag_context: Optional[List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """Analyze using Ollama local model (optimized for edge devices)"""
    import json
    from app.core.edge_optimization import is_edge_device, get_optimal_model_size
    
    # Use optimal model based on device type
    is_edge = is_edge_device()
    if is_edge:
        # Edge device: Use qwen:0.5b (fastest)
        model_name = get_optimal_model_size()  # Returns qwen:0.5b for edge
        logger.info("Using edge-optimized model", model=model_name, device="edge")
    else:
        # Laptop: Use llama3.2:3b (better quality, user's downloaded model)
        model_name = settings.OLLAMA_MODEL
        # If user has qwen:0.5b set, override to llama3.2:3b for laptops
        if model_name == "qwen:0.5b":
            model_name = "llama3.2:3b"
            logger.info("Overriding to llama3.2:3b for laptop", original=settings.OLLAMA_MODEL)
        logger.info("Using laptop model", model=model_name, device="laptop")
    
    # Build optimized prompts
    system_prompt = build_system_prompt(domain, user_context, language)
    user_prompt = build_user_prompt(query_text, rag_context, language)
    
    # Call Ollama API with optimized settings for speed
    timeout = 180.0 if is_edge else 120.0  # More time for edge devices
    
    # Aggressive speed optimizations: much shorter responses, minimal context
    num_predict = 800 if is_edge else 1200  # Very short responses = much faster
    temperature = 0.1  # Lower = faster and more consistent
    num_ctx = 1024  # Smaller context window = faster processing
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "format": "json",  # Request JSON response
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,  # Very short responses = faster
                    "num_ctx": num_ctx,  # Smaller context window = faster
                    "repeat_penalty": 1.1,  # Prevent repetition
                    "top_k": 20,  # Reduce sampling options = faster
                    "top_p": 0.9,  # Narrower sampling = faster
                    "tfs_z": 1.0,  # Tail free sampling
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        result = response.json()
        content = result.get("message", {}).get("content", "{}")
        
        # Parse JSON response
        try:
            analysis_result = json.loads(content)
            # Validate and normalize the response
            analysis_result = normalize_ollama_response(analysis_result, query_text)
        except json.JSONDecodeError as e:
            logger.warning("Ollama returned invalid JSON, using fallback", error=str(e), content=content[:200])
            # If not JSON, create structured response from text
            analysis_result = create_structured_response_from_text(content, query_text)
        
        return analysis_result


def normalize_ollama_response(response: Dict[str, Any], query_text: str) -> Dict[str, Any]:
    """Normalize Ollama response to ensure all required fields exist with correct types"""
    # Ensure risk_score is int
    risk_score = response.get("risk_score", 50)
    if isinstance(risk_score, str):
        try:
            risk_score = int(risk_score)
        except ValueError:
            risk_score = 50
    
    # Ensure lists are actually lists
    def ensure_list(value, default=[]):
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return [value] if value else default
        else:
            return default
    
    # Ensure bool is actually bool
    lawyer_consultation = response.get("lawyer_consultation_recommended", True)
    if isinstance(lawyer_consultation, str):
        lawyer_consultation = lawyer_consultation.lower() in ["true", "yes", "1"]
    
    normalized = {
        "risk_level": response.get("risk_level", "medium"),
        "risk_score": risk_score,
        "risk_explanation": response.get("risk_explanation", "Risk assessment provided"),
        "analysis": response.get("analysis", "Analysis not available"),
        "pros": ensure_list(response.get("pros")),
        "cons": ensure_list(response.get("cons")),
        "preventive_roadmap": ensure_list(response.get("preventive_roadmap"), [{"step_number": 1, "action": "Review analysis", "importance": "Important"}]),
        "legal_references": ensure_list(response.get("legal_references")),
        "warnings": ensure_list(response.get("warnings")),
        "lawyer_consultation_recommended": bool(lawyer_consultation),
        "next_steps": ensure_list(response.get("next_steps")),
    }
    
    return normalized


def build_system_prompt(domain: str, user_context: Optional[Dict[str, Any]], language: str) -> str:
    """
    Build ultra-minimal system prompt for fastest inference
    """
    # Minimal prompt - just the essentials
    prompt = f"""Legal advisor for {domain} law in India. Return JSON only:

{{
    "risk_level": "low|medium|high",
    "risk_score": 0-100,
    "risk_explanation": "brief",
    "analysis": "short explanation (max 100 words)",
    "pros": ["pro1", "pro2"],
    "cons": ["con1", "con2"],
    "preventive_roadmap": [{{"step_number": 1, "action": "action", "importance": "why"}}],
    "legal_references": [{{"act_name": "Act", "section_number": "Sec", "summary": "brief", "relevance": "relevance"}}],
    "warnings": ["warning1"],
    "lawyer_consultation_recommended": true/false,
    "next_steps": ["step1", "step2"]
}}

Be very brief. Max 100 words."""
    
    return prompt


def build_user_prompt(query_text: str, rag_context: Optional[List[Dict[str, Any]]], language: str) -> str:
    """Build ultra-minimal user prompt for fastest inference"""
    # Skip RAG context in offline mode for speed (optional - can enable if needed)
    # For maximum speed, skip context entirely
    prompt = f"Q: {query_text}\n\nReturn JSON only."
    
    # Optionally include minimal context (comment out for absolute fastest)
    # if rag_context:
    #     prompt += "\nContext: " + rag_context[0].get('text', '')[:100] if rag_context else ""
    
    return prompt


def create_structured_response_from_text(text: str, query_text: str) -> Dict[str, Any]:
    """Create structured response from plain text (fallback)"""
    return {
        "risk_level": "medium",
        "risk_score": 50,
        "risk_explanation": "Analysis based on provided context",
        "analysis": text[:1000],  # Limit length
        "pros": [],
        "cons": [],
        "preventive_roadmap": [
            {
                "step_number": 1,
                "action": "Review the analysis provided",
                "importance": "Understanding your legal situation is the first step"
            }
        ],
        "legal_references": [],
        "warnings": ["This is an automated analysis. Consult a lawyer for complex matters."],
        "lawyer_consultation_recommended": True,
        "next_steps": ["Review the analysis", "Consider professional consultation"]
    }


async def analyze_legal_query_with_fallback(
    query_text: str,
    domain: str,
    user_context: Optional[Dict[str, Any]] = None,
    language: str = "en",
    rag_context: Optional[List[Dict[str, Any]]] = None,
    prefer_online: bool = True
) -> Dict[str, Any]:
    """
    Analyze legal query - OpenAI ONLY mode for fastest responses
    
    Args:
        prefer_online: Ignored - always uses OpenAI if available
    """
    # FORCE OpenAI ONLY - Skip all Ollama checks for maximum speed
    if settings.USE_OFFLINE_MODE:
        # If offline mode is explicitly enabled, still check OpenAI first
        logger.warning("Offline mode enabled but forcing OpenAI check for speed")
    
    # Check OpenAI immediately - no Ollama fallback
    if not settings.OPENAI_API_KEY:
        raise Exception("OpenAI API key is required. Please set OPENAI_API_KEY in .env file")
    
    # Quick OpenAI check (1 second timeout for speed)
    try:
        openai_available = await asyncio.wait_for(check_openai_connection(), timeout=1.0)
        if openai_available:
            # Direct OpenAI call - no logging for speed
            return await analyze_with_openai(query_text, domain, user_context, language, rag_context)
        else:
            raise Exception("OpenAI API is not accessible. Check your API key and internet connection.")
    except asyncio.TimeoutError:
        # Even on timeout, try OpenAI directly (might be slow network but still work)
        logger.warning("OpenAI check timed out, trying OpenAI directly anyway")
        try:
            return await analyze_with_openai(query_text, domain, user_context, language, rag_context)
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}. Check your API key and internet connection.")
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}. Check your API key and internet connection.")

