"""
Redis client configuration with LangCache support
"""
import redis.asyncio as redis
from app.core.config import settings
import structlog

logger = structlog.get_logger()

redis_client: redis.Redis = None
langcache_client = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client, langcache_client
    
    try:
        # Use Redis Labs cloud instance if configured
        if hasattr(settings, 'REDIS_HOST') and settings.REDIS_HOST:
            redis_client = await redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                ssl=True if settings.REDIS_PORT == 11431 else False
            )
        else:
            # Fallback to URL-based connection
            redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        
        await redis_client.ping()
        logger.info("Redis connected successfully")
        
        # Initialize LangCache if API key is provided
        if hasattr(settings, 'LANGCACHE_API_KEY') and settings.LANGCACHE_API_KEY:
            try:
                from langcache import LangCache
                langcache_client = LangCache(
                    api_key=settings.LANGCACHE_API_KEY,
                    redis_client=redis_client
                )
                logger.info("LangCache initialized successfully")
            except ImportError:
                logger.warning("LangCache not installed. Install with: pip install langcache")
            except Exception as e:
                logger.warning("LangCache initialization failed", error=str(e))
        
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        redis_client = None


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    if redis_client is None:
        await init_redis()
    return redis_client


def get_langcache():
    """Get LangCache client"""
    return langcache_client

