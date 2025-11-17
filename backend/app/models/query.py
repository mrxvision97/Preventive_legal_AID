"""
Query model
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum


class LegalDomain(str, enum.Enum):
    """Legal domain enumeration"""
    AGRICULTURE = "agriculture"
    CIVIL = "civil"
    FAMILY = "family"
    UNIVERSITY = "university"


class UrgencyLevel(str, enum.Enum):
    """Urgency level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class QueryStatus(str, enum.Enum):
    """Query status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Query(Base):
    """Query model"""
    __tablename__ = "queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    domain = Column(SQLEnum(LegalDomain), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_language = Column(String(10), default="en")
    urgency_level = Column(SQLEnum(UrgencyLevel), default=UrgencyLevel.MEDIUM)
    location = Column(JSONB, nullable=True)
    user_context = Column(JSONB, nullable=True)  # Additional context
    document_url = Column(String(500), nullable=True)  # S3 URL
    audio_url = Column(String(500), nullable=True)  # S3 URL
    status = Column(SQLEnum(QueryStatus), default=QueryStatus.PENDING, index=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", backref="queries")
    ai_response = relationship("AIResponse", back_populates="query", uselist=False)
    feedback = relationship("Feedback", back_populates="query", uselist=False)

