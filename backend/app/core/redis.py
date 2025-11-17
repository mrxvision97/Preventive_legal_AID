"""
Redis client configuration
"""
import redis.asyncio as redis
from app.core.config import settings
import structlog

logger = structlog.get_logger()

redis_client: redis.Redis = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        redis_client = None


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    if redis_client is None:
        await init_redis()
    return redis_client

