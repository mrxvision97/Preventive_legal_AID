"""
User model
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum


class UserType(str, enum.Enum):
    """User type enumeration"""
    FARMER = "farmer"
    STUDENT = "student"
    CITIZEN = "citizen"
    ADMIN = "admin"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(15), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False, default=UserType.CITIZEN)
    language_preference = Column(String(10), default="hi")  # Hindi by default
    location = Column(JSONB, nullable=True)  # {city, state, pincode, coordinates}
    preferences = Column(JSONB, default={})  # User settings
    query_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

