"""
AI Response model
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AIResponse(Base):
    """AI Response model"""
    __tablename__ = "ai_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id"), unique=True, nullable=False, index=True)
    
    # Risk Assessment
    risk_level = Column(String(20), nullable=False)  # low, medium, high
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_explanation = Column(Text, nullable=False)
    
    # Analysis
    analysis = Column(Text, nullable=False)
    
    # Pros and Cons
    pros = Column(JSONB, nullable=True)  # Array of strings
    cons = Column(JSONB, nullable=True)  # Array of strings
    
    # Preventive Roadmap
    preventive_roadmap = Column(JSONB, nullable=True)  # Array of step objects
    
    # Legal References
    legal_references = Column(JSONB, nullable=True)  # Array of reference objects
    
    # Warnings and Next Steps
    warnings = Column(JSONB, nullable=True)  # Array of strings
    next_steps = Column(JSONB, nullable=True)  # Array of strings
    
    # Metadata
    citations = Column(JSONB, nullable=True)  # RAG sources
    confidence_score = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    lawyer_consultation_recommended = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    query = relationship("Query", back_populates="ai_response")

