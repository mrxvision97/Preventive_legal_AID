"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Load .env file from backend directory
    env_file: str = str(Path(__file__).parent.parent / ".env")
    env_file_encoding: str = "utf-8"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    # Application
    APP_NAME: str = "VU Legal AID"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/legal_db"
    DATABASE_ECHO: bool = False
    
    # Redis (Redis Labs Cloud)
    REDIS_HOST: str = "redis-11431.c305.ap-south-1-1.ec2.cloud.redislabs.com"
    REDIS_PORT: int = 11431
    REDIS_USERNAME: str = "default"
    REDIS_PASSWORD: str = "QtdXhZHAhwe11zCjqLOm1UkU8ud9o5qi"  # Default, override from secrets
    REDIS_URL: str = ""  # Fallback URL
    REDIS_CACHE_TTL: int = 3600
    
    # LangCache
    LANGCACHE_API_KEY: str = "wy4ECQMIU-DhqXrfFongfMQbzYOkOOk8mZnvYVY1VvFvfW2MVr3thSzCSr2JFdK20oIBgOvV5BEyOESlCny_6_M2dqKjEGU9I470l0GLIwgsugntnP9DthQK71uInD3eUgNFecMTloBm5DK7r0GupYTHXx67wCXBPPOt_YMkppOOu2G-ziWa3h7iHHyjWDicKKBtwxRZQT8lYv4VDWA2wegLyk409A0SqRfNwp687eNrKWT1"  # Default, override from secrets
    
    # Ollama (Offline Mode)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"  # Default for laptops. Auto-changed to qwen:0.5b on edge devices
    USE_OFFLINE_MODE: bool = False  # Force offline mode
    FORCE_EDGE_MODE: bool = False  # Force edge device mode even on laptops (for testing)
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenAI - Optimized for speed (faster responses)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # Faster model (change to "gpt-4o" for better quality but slower)
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_TEMPERATURE: float = 0.3  # Lower = faster + more consistent
    OPENAI_MAX_TOKENS: int = 2000  # Reduced for faster responses (increase to 4000 for longer responses)
    
    # RAG Settings - DISABLED for speed
    ENABLE_RAG: bool = False  # Set to True to enable RAG/embeddings (slower but more accurate)
    
    # Vector Database
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "legal-knowledge-base"
    
    # Weaviate (Alternative)
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: str = ""
    
    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "legal-documents-bucket"
    S3_PRESIGNED_URL_EXPIRATION: int = 604800  # 7 days
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_AI_PER_HOUR: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@legalai.com"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".jpg", ".jpeg", ".png", ".webm", ".mp3", ".wav"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

