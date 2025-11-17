"""
Legal Aid Center model
"""
from sqlalchemy import Column, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class LegalAidCenter(Base):
    """Legal Aid Center model"""
    __tablename__ = "legal_aid_centers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    pincode = Column(String(10), nullable=False, index=True)
    phone = Column(String(15), nullable=True)
    email = Column(String(255), nullable=True)
    services = Column(ARRAY(String), nullable=True)  # Array of service strings
    operating_hours = Column(String(500), nullable=True)  # JSON string or text
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

