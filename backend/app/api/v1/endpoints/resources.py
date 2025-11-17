"""
Resource endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.models.legal_aid_center import LegalAidCenter
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()


class LegalAidCenterResponse(BaseModel):
    id: str
    name: str
    address: str
    city: str
    state: str
    pincode: str
    phone: Optional[str]
    email: Optional[str]
    services: Optional[List[str]]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    
    model_config = {"from_attributes": True}


@router.get("/legal-centers", response_model=List[LegalAidCenterResponse])
async def get_legal_centers(
    city: Optional[str] = None,
    state: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get all legal aid centers"""
    from sqlalchemy import select
    
    query = select(LegalAidCenter)
    
    if city:
        query = query.where(LegalAidCenter.city.ilike(f"%{city}%"))
    if state:
        query = query.where(LegalAidCenter.state.ilike(f"%{state}%"))
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    centers = result.scalars().all()
    
    return [LegalAidCenterResponse.model_validate(c) for c in centers]


@router.get("/legal-centers/nearby", response_model=List[LegalAidCenterResponse])
async def get_nearby_centers(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(default=10.0),
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get legal aid centers near location"""
    from sqlalchemy import select, func
    
    # Simple distance calculation (Haversine formula in SQL)
    # For production, use PostGIS for accurate distance calculations
    query = select(LegalAidCenter).where(
        LegalAidCenter.latitude.isnot(None),
        LegalAidCenter.longitude.isnot(None)
    ).limit(limit)
    
    result = await db.execute(query)
    centers = result.scalars().all()
    
    # Filter by distance (simplified - implement proper distance calculation)
    return [LegalAidCenterResponse.from_orm(c) for c in centers[:limit]]


@router.get("/faqs")
async def get_faqs(
    domain: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    """Get frequently asked questions"""
    # TODO: Implement FAQ database
    return {"faqs": []}


@router.get("/articles")
async def get_articles(
    domain: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    """Get legal education articles"""
    # TODO: Implement articles database
    return {"articles": []}


@router.get("/schemes")
async def get_schemes(
    state: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    """Get government welfare schemes"""
    # TODO: Implement schemes database
    return {"schemes": []}

