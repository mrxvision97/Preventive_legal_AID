"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
# Database initialization commented out - running without DB
# from app.core.database import init_db
from app.api.v1.router import api_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting application", app_name=settings.APP_NAME)
    
    # Load secrets from cloud storage
    try:
        from app.services.cloud_secrets import load_secrets
        await load_secrets()
    except Exception as e:
        logger.warning("Secrets loading failed, using defaults", error=str(e))
    
    # Initialize database (commented out for now - running without DB)
    # await init_db()
    
    # Initialize Redis
    try:
        from app.core.redis import init_redis
        await init_redis()
    except Exception as e:
        logger.warning("Redis initialization skipped", error=str(e))
    
    # Initialize Pinecone
    try:
        from app.services.pinecone_service import init_pinecone
        await init_pinecone()
    except Exception as e:
        logger.warning("Pinecone initialization skipped", error=str(e))
    
    # Log device detection and optimizations
    try:
        from app.core.edge_optimization import is_edge_device, optimize_for_edge
        is_edge = is_edge_device()
        if is_edge:
            optimizations = optimize_for_edge()
            logger.info("Edge device detected (Jetson Nano) - optimizations applied", **optimizations)
        else:
            logger.info("Laptop/Desktop detected - using full-featured models (OpenAI preferred)")
    except Exception as e:
        logger.debug("Device detection check failed", error=str(e))
    
    logger.info("Application started successfully")
    yield
    # Shutdown
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered legal guidance platform for preventive legal assistance",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
)

# Custom Middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VU Legal AID API",
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

