"""
Query processing endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.query import Query, QueryStatus, LegalDomain, UrgencyLevel
from app.models.ai_response import AIResponse
from app.schemas.query import QueryCreate, QueryResponse, QueryWithResponse
from app.api.v1.endpoints.auth import get_current_user
from app.services.ai_service import analyze_legal_query
from app.services.rag_service import retrieve_relevant_context
from datetime import datetime
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def create_query(
    query_data: QueryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """Submit a new legal query"""
    # Create query record
    query = Query(
        user_id=current_user.id,
        domain=query_data.domain,
        query_text=query_data.query_text,
        query_language=query_data.query_language,
        urgency_level=query_data.urgency_level,
        location=query_data.location,
        user_context=query_data.user_context,
        document_url=query_data.document_url,
        audio_url=query_data.audio_url,
        status=QueryStatus.PROCESSING,
        processing_started_at=datetime.utcnow(),
    )
    
    db.add(query)
    await db.commit()
    await db.refresh(query)
    
    # Update user query count
    current_user.query_count += 1
    await db.commit()
    
    # Process query in background
    if background_tasks:
        background_tasks.add_task(process_query_async, str(query.id))
    
    logger.info("Query created", query_id=str(query.id), user_id=str(current_user.id))
    
    return QueryResponse.model_validate(query)


async def process_query_async(query_id: str):
    """Process query asynchronously"""
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        # Get query
        result = await db.execute(select(Query).where(Query.id == UUID(query_id)))
        query = result.scalar_one_or_none()
        
        if not query:
            logger.error("Query not found", query_id=query_id)
            return
        
        try:
            # Retrieve RAG context
            rag_context = await retrieve_relevant_context(
                query.query_text,
                domain=query.domain.value,
                location_filter=query.location
            )
            
            # Build user context
            user_context = {
                "user_type": query.user.user_type.value,
                "location": query.location or {},
            }
            
            # Analyze with AI
            analysis_result = await analyze_legal_query(
                query_text=query.query_text,
                domain=query.domain.value,
                user_context=user_context,
                language=query.query_language,
                rag_context=rag_context,
            )
            
            # Save AI response
            ai_response = AIResponse(
                query_id=query.id,
                risk_level=analysis_result["risk_level"],
                risk_score=analysis_result["risk_score"],
                risk_explanation=analysis_result["risk_explanation"],
                analysis=analysis_result["analysis"],
                pros=analysis_result["pros"],
                cons=analysis_result["cons"],
                preventive_roadmap=analysis_result["preventive_roadmap"],
                legal_references=analysis_result["legal_references"],
                warnings=analysis_result["warnings"],
                next_steps=analysis_result["next_steps"],
                citations=[ctx.get("metadata", {}) for ctx in rag_context],
                confidence_score=analysis_result.get("confidence_score"),
                model_version=analysis_result.get("model_version"),
                processing_time_ms=analysis_result.get("processing_time_ms"),
                tokens_used=analysis_result.get("tokens_used"),
                lawyer_consultation_recommended=analysis_result["lawyer_consultation_recommended"],
            )
            
            db.add(ai_response)
            
            # Update query status
            query.status = QueryStatus.COMPLETED
            query.processing_completed_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info("Query processed successfully", query_id=query_id)
            
        except Exception as e:
            logger.error("Query processing failed", query_id=query_id, error=str(e))
            query.status = QueryStatus.FAILED
            await db.commit()


@router.get("/{query_id}", response_model=QueryWithResponse)
async def get_query(
    query_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific query with AI response"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Query).where(Query.id == query_id, Query.user_id == current_user.id)
    )
    query = result.scalar_one_or_none()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Get AI response if exists
    result = await db.execute(
        select(AIResponse).where(AIResponse.query_id == query_id)
    )
    ai_response = result.scalar_one_or_none()
    
    response_data = QueryWithResponse.model_validate(query)
    if ai_response:
        response_data.ai_response = {
            "risk_level": ai_response.risk_level,
            "risk_score": ai_response.risk_score,
            "risk_explanation": ai_response.risk_explanation,
            "analysis": ai_response.analysis,
            "pros": ai_response.pros,
            "cons": ai_response.cons,
            "preventive_roadmap": ai_response.preventive_roadmap,
            "legal_references": ai_response.legal_references,
            "warnings": ai_response.warnings,
            "next_steps": ai_response.next_steps,
            "citations": ai_response.citations,
            "lawyer_consultation_recommended": ai_response.lawyer_consultation_recommended,
        }
    
    return response_data


@router.get("", response_model=List[QueryResponse])
async def get_queries(
    skip: int = 0,
    limit: int = 10,
    domain: Optional[LegalDomain] = None,
    status_filter: Optional[QueryStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's query history"""
    from sqlalchemy import select
    
    query = select(Query).where(Query.user_id == current_user.id)
    
    if domain:
        query = query.where(Query.domain == domain)
    if status_filter:
        query = query.where(Query.status == status_filter)
    
    query = query.order_by(Query.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    queries = result.scalars().all()
    
    return [QueryResponse.model_validate(q) for q in queries]


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_query(
    query_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a query"""
    from sqlalchemy import select, delete
    
    # Check ownership
    result = await db.execute(
        select(Query).where(Query.id == query_id, Query.user_id == current_user.id)
    )
    query = result.scalar_one_or_none()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Delete AI response if exists
    from sqlalchemy import delete
    await db.execute(delete(AIResponse).where(AIResponse.query_id == query_id))
    
    # Delete query
    await db.delete(query)
    await db.commit()
    
    return None

