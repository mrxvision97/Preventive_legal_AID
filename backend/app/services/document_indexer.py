"""
Document indexing service for knowledge base
"""
import PyPDF2
import pdfplumber
from typing import List, Dict, Any
from app.services.rag_service import index_document
import structlog

logger = structlog.get_logger()


async def index_pdf_document(
    file_path: str,
    domain: str,
    metadata: Dict[str, Any]
) -> bool:
    """
    Extract text from PDF and index it
    
    Args:
        file_path: Path to PDF file
        domain: Legal domain (agriculture, civil, family, university)
        metadata: Document metadata
        
    Returns:
        Success status
    """
    try:
        text_content = ""
        
        # Try pdfplumber first (better for complex PDFs)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() or ""
        except Exception:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
        
        if not text_content.strip():
            logger.warning("No text extracted from PDF", file_path=file_path)
            return False
        
        # Clean text
        text_content = clean_text(text_content)
        
        # Index document
        success = await index_document(
            text=text_content,
            metadata=metadata,
            domain=domain
        )
        
        logger.info("PDF indexed", file_path=file_path, domain=domain, success=success)
        return success
        
    except Exception as e:
        logger.error("PDF indexing failed", file_path=file_path, error=str(e))
        return False


async def index_text_document(
    text: str,
    domain: str,
    metadata: Dict[str, Any]
) -> bool:
    """
    Index plain text document
    
    Args:
        text: Document text
        domain: Legal domain
        metadata: Document metadata
        
    Returns:
        Success status
    """
    try:
        cleaned_text = clean_text(text)
        success = await index_document(
            text=cleaned_text,
            metadata=metadata,
            domain=domain
        )
        
        logger.info("Text document indexed", domain=domain, success=success)
        return success
        
    except Exception as e:
        logger.error("Text indexing failed", error=str(e))
        return False


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters but keep legal symbols
    # Keep: periods, commas, colons, semicolons, parentheses, brackets
    
    return text.strip()

