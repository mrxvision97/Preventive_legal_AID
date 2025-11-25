"""
Main API router
"""
from fastapi import APIRouter

# Only import endpoints that don't require database
from app.api.v1.endpoints import public, ai, voice_status

# DB-related endpoints commented out - running without DB
# These imports would fail because models depend on Base which is None
# from app.api.v1.endpoints import auth, users, queries, resources, admin, feedback, knowledge_base

api_router = APIRouter()

# Include only non-DB endpoints
api_router.include_router(public.router, prefix="/public", tags=["Public"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(voice_status.router, prefix="/ai", tags=["AI"])

# DB-related endpoints commented out - running without DB
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(queries.router, prefix="/queries", tags=["Queries"])
# api_router.include_router(feedback.router, prefix="/queries", tags=["Feedback"])
# api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
# api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
# api_router.include_router(knowledge_base.router, prefix="/admin/knowledge-base", tags=["Knowledge Base"])

