"""
Main API router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, queries, ai, resources, admin, feedback, public, knowledge_base

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(public.router, prefix="/public", tags=["Public"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(queries.router, prefix="/queries", tags=["Queries"])
api_router.include_router(feedback.router, prefix="/queries", tags=["Feedback"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(resources.router, prefix="/resources", tags=["Resources"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(knowledge_base.router, prefix="/admin/knowledge-base", tags=["Knowledge Base"])

