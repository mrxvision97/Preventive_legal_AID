"""
Feedback endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.query import Query
from app.models.feedback import Feedback
from app.api.v1.endpoints.auth import get_current_user
import structlog

logger = structlog.get_logger()
router = APIRouter()


class FeedbackCreate(BaseModel):
    rating: int  # 1-5
    was_helpful: bool
    comments: str = None


@router.post("/{query_id}/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    query_id: UUID,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for a query"""
    from sqlalchemy import select
    
    # Verify query exists and belongs to user
    result = await db.execute(
        select(Query).where(Query.id == query_id, Query.user_id == current_user.id)
    )
    query = result.scalar_one_or_none()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check if feedback already exists
    result = await db.execute(
        select(Feedback).where(Feedback.query_id == query_id)
    )
    existing_feedback = result.scalar_one_or_none()
    
    if existing_feedback:
        # Update existing feedback
        existing_feedback.rating = feedback_data.rating
        existing_feedback.was_helpful = feedback_data.was_helpful
        existing_feedback.comments = feedback_data.comments
    else:
        # Create new feedback
        feedback = Feedback(
            query_id=query_id,
            user_id=current_user.id,
            rating=feedback_data.rating,
            was_helpful=feedback_data.was_helpful,
            comments=feedback_data.comments,
        )
        db.add(feedback)
    
    await db.commit()
    
    logger.info("Feedback submitted", query_id=str(query_id), user_id=str(current_user.id))
    
    return {"message": "Feedback submitted successfully"}

