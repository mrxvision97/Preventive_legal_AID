"""
Voice service status endpoint
"""
from fastapi import APIRouter
# DB/Auth imports commented out - running without DB
# from app.api.v1.endpoints.auth import get_current_user
# from app.models.user import User
from app.services.offline_voice_service import get_voice_service_status

router = APIRouter()


@router.get("/voice-status")
async def get_voice_status(
    # current_user removed - public endpoint (no DB required)
):
    """Get status of voice services (online/offline) - Public endpoint"""
    status = await get_voice_service_status()
    return status

