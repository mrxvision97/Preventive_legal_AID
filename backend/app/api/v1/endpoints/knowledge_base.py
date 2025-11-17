"""
Knowledge base management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import tempfile
import os

from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.services.document_indexer import index_pdf_document, index_text_document
import structlog

logger = structlog.get_logger()
router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    from app.models.user import UserType
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


class IndexDocumentRequest(BaseModel):
    domain: str  # agriculture, civil, family, university
    source_name: str
    section_number: Optional[str] = None
    language: str = "en"
    location: Optional[str] = None
    publication_date: Optional[str] = None
    issuing_authority: Optional[str] = None


@router.post("/index-document")
async def index_document_endpoint(
    file: UploadFile = File(...),
    domain: str = None,
    source_name: str = None,
    admin: User = Depends(require_admin),
):
    """Index a document to the knowledge base"""
    if not domain or not source_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="domain and source_name are required"
        )
    
    # Save uploaded file temporarily
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in ['pdf', 'txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported"
        )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        metadata = {
            "source": source_name,
            "filename": file.filename,
            "domain": domain,
        }
        
        if file_extension == 'pdf':
            success = await index_pdf_document(tmp_path, domain, metadata)
        else:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                text = f.read()
            success = await index_text_document(text, domain, metadata)
        
        if success:
            return {"message": "Document indexed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to index document"
            )
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

