"""
Admin endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any

from app.core.database import get_db
from app.models.user import User, UserType
from app.models.query import Query
from app.models.feedback import Feedback
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import UserType as UserTypeEnum

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.user_type != UserTypeEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/analytics")
async def get_analytics(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get system analytics"""
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    # Queries today
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    result = await db.execute(
        select(func.count(Query.id)).where(
            func.date(Query.created_at) == today
        )
    )
    queries_today = result.scalar()
    
    # Average processing time
    from app.models.ai_response import AIResponse
    result = await db.execute(
        select(func.avg(AIResponse.processing_time_ms))
    )
    avg_processing_time = result.scalar() or 0
    
    # User satisfaction
    result = await db.execute(
        select(func.avg(Feedback.rating))
    )
    avg_rating = result.scalar() or 0
    
    return {
        "total_users": total_users,
        "queries_today": queries_today,
        "average_processing_time_ms": float(avg_processing_time),
        "average_rating": float(avg_rating),
    }


@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all users"""
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    
    from app.schemas.user import UserResponse
    return [UserResponse.model_validate(u) for u in users]


@router.get("/queries")
async def get_all_queries(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all queries"""
    result = await db.execute(
        select(Query).order_by(Query.created_at.desc()).offset(skip).limit(limit)
    )
    queries = result.scalars().all()
    
    from app.schemas.query import QueryResponse
    return [QueryResponse.model_validate(q) for q in queries]


@router.get("/system-health")
async def get_system_health(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get system health status"""
    health = {
        "database": "healthy",
        "redis": "unknown",
        "openai": "unknown",
        "vector_db": "unknown",
    }
    
    # Check database
    try:
        await db.execute(select(1))
    except Exception:
        health["database"] = "unhealthy"
    
    # TODO: Check Redis, OpenAI, Vector DB
    
    return health

