"""
Database configuration and session management
COMMENTED OUT - Running without database
"""
# Database functionality commented out - running without DB
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from sqlalchemy.orm import declarative_base
# from app.core.config import settings
# import structlog

# logger = structlog.get_logger()

# # Create async engine
# engine = create_async_engine(
#     settings.DATABASE_URL,
#     echo=settings.DATABASE_ECHO,
#     future=True,
#     pool_pre_ping=True,
#     pool_size=10,
#     max_overflow=20,
# )

# # Create async session factory
# AsyncSessionLocal = async_sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autocommit=False,
#     autoflush=False,
# )

# # Base class for models
# Base = declarative_base()


# async def get_db() -> AsyncSession:
#     """Dependency for getting database session"""
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()


# async def init_db():
#     """Initialize database - create tables and extensions"""
#     try:
#         # Import all models to register them
#         from app.models import user, query, ai_response, feedback, legal_aid_center
#         
#         # Create tables
#         async with engine.begin() as conn:
#             # Install pgvector extension
#             await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
#             # Create all tables
#             await conn.run_sync(Base.metadata.create_all)
#         
#         logger.info("Database initialized successfully")
#     except Exception as e:
#         logger.error("Database initialization failed", error=str(e))
#         raise

# Placeholder for compatibility
Base = None
engine = None
AsyncSessionLocal = None

async def get_db():
    """Placeholder - DB disabled"""
    raise NotImplementedError("Database is disabled. This endpoint requires DB functionality.")

async def init_db():
    """Placeholder - DB disabled"""
    pass

