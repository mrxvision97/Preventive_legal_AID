"""
OCR Service for extracting text from images
Uses OpenAI Vision API (primary) or Tesseract (fallback)
"""
import base64
import io
from typing import Optional, Dict, Any
from PIL import Image
import structlog
from app.core.config import settings

logger = structlog.get_logger()

# Try to import Tesseract (optional fallback)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract not available - using OpenAI Vision only")


async def extract_text_from_image(
    image_data: bytes,
    use_openai: bool = True
) -> Dict[str, Any]:
    """
    Extract text from image using OCR
    
    Args:
        image_data: Image file bytes
        use_openai: If True, use OpenAI Vision API (better quality). If False, use Tesseract.
    
    Returns:
        Dict with extracted_text, confidence, method_used
    """
    try:
        # Try OpenAI Vision API first (if available and enabled)
        if use_openai and settings.OPENAI_API_KEY:
            try:
                return await _extract_with_openai_vision(image_data)
            except Exception as e:
                logger.warning("OpenAI Vision failed, trying Tesseract", error=str(e))
                if TESSERACT_AVAILABLE:
                    return await _extract_with_tesseract(image_data)
                else:
                    raise Exception("OpenAI Vision failed and Tesseract not available")
        
        # Fallback to Tesseract
        if TESSERACT_AVAILABLE:
            return await _extract_with_tesseract(image_data)
        else:
            raise Exception("No OCR method available. Set OPENAI_API_KEY or install Tesseract.")
            
    except Exception as e:
        logger.error("OCR extraction failed", error=str(e))
        raise


async def _extract_with_openai_vision(image_data: bytes) -> Dict[str, Any]:
    """Extract text using OpenAI Vision API"""
    from openai import OpenAI
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Convert image to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Determine image format
    image = Image.open(io.BytesIO(image_data))
    format_map = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp',
    }
    mime_type = format_map.get(image.format, 'image/jpeg')
    
    # Use OpenAI Vision API
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Fast and cost-effective
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all text from this image. Preserve the structure, formatting, and context. Include all numbers, dates, names, addresses, and legal terms. If this is a legal document, identify the document type (contract, notice, certificate, etc.) and key information."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=2000,
        temperature=0.1,  # Low temperature for accurate extraction
    )
    
    extracted_text = response.choices[0].message.content
    
    # Classify document type and extract key info
    classification = await _classify_document(extracted_text)
    
    return {
        "extracted_text": extracted_text,
        "confidence": 0.95,  # OpenAI Vision is highly accurate
        "method_used": "openai_vision",
        "document_type": classification.get("document_type", "unknown"),
        "key_information": classification.get("key_information", {}),
        "language": classification.get("language", "en"),
    }


async def _extract_with_tesseract(image_data: bytes) -> Dict[str, Any]:
    """Extract text using Tesseract OCR (offline fallback)"""
    try:
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Extract text
        extracted_text = pytesseract.image_to_string(image, lang='eng+hin')  # English + Hindi
        
        # Get confidence data
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.5
        
        # Classify document
        classification = await _classify_document(extracted_text)
        
        return {
            "extracted_text": extracted_text,
            "confidence": avg_confidence,
            "method_used": "tesseract",
            "document_type": classification.get("document_type", "unknown"),
            "key_information": classification.get("key_information", {}),
            "language": classification.get("language", "en"),
        }
    except Exception as e:
        logger.error("Tesseract OCR failed", error=str(e))
        raise Exception(f"Tesseract OCR failed: {str(e)}")


async def _classify_document(text: str) -> Dict[str, Any]:
    """
    Classify document type and extract key information using AI
    """
    if not settings.OPENAI_API_KEY:
        # Simple rule-based classification if no OpenAI
        return {
            "document_type": "unknown",
            "key_information": {},
            "language": "en"
        }
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Use AI to classify and extract key info
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal document classifier. Analyze the extracted text and return JSON with: document_type (contract, notice, certificate, invoice, legal_document, etc.), key_information (dates, names, amounts, addresses, legal terms), and language (en, hi, etc.)."
                },
                {
                    "role": "user",
                    "content": f"Classify this document and extract key information:\n\n{text[:2000]}"  # Limit text length
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.1,
        )
        
        import json
        classification = json.loads(response.choices[0].message.content)
        return classification
        
    except Exception as e:
        logger.warning("Document classification failed", error=str(e))
        return {
            "document_type": "unknown",
            "key_information": {},
            "language": "en"
        }

