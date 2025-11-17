"""
Query schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.query import LegalDomain, UrgencyLevel, QueryStatus


class QueryCreate(BaseModel):
    domain: LegalDomain
    query_text: str
    query_language: str = "en"
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM
    location: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None
    document_url: Optional[str] = None
    audio_url: Optional[str] = None


class QueryResponse(BaseModel):
    id: str
    user_id: str
    domain: LegalDomain
    query_text: str
    query_language: str
    urgency_level: UrgencyLevel
    status: QueryStatus
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class QueryWithResponse(QueryResponse):
    ai_response: Optional[Dict[str, Any]] = None

