"""
Cloud Secrets Manager for storing API keys securely
Supports AWS Secrets Manager, Azure Key Vault, or environment variables
"""
from typing import Optional, Dict, Any
from app.core.config import settings
import structlog
import os

logger = structlog.get_logger()

# Try importing AWS Secrets Manager
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None


async def get_secret_from_aws(secret_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve secret from AWS Secrets Manager"""
    if not AWS_AVAILABLE or not settings.AWS_ACCESS_KEY_ID:
        return None
    
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        response = client.get_secret_value(SecretId=secret_name)
        import json
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error("AWS Secrets Manager error", error=str(e))
        return None
    except Exception as e:
        logger.error("Failed to retrieve secret from AWS", error=str(e))
        return None


async def load_secrets():
    """
    Load secrets from cloud storage or environment variables
    Priority: AWS Secrets Manager > Environment Variables > Config defaults
    """
    secrets = {}
    
    # Try AWS Secrets Manager first
    if AWS_AVAILABLE and settings.AWS_ACCESS_KEY_ID:
        aws_secrets = await get_secret_from_aws("vu-legal-aid-secrets")
        if aws_secrets:
            secrets.update(aws_secrets)
            logger.info("Loaded secrets from AWS Secrets Manager")
    
    # Fallback to environment variables
    env_secrets = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", ""),
        "LANGCACHE_API_KEY": os.getenv("LANGCACHE_API_KEY", ""),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY", ""),
    }
    
    # Update secrets with environment variables (if not already set from AWS)
    for key, value in env_secrets.items():
        if value and key not in secrets:
            secrets[key] = value
    
    # Update settings with loaded secrets
    if secrets.get("OPENAI_API_KEY"):
        settings.OPENAI_API_KEY = secrets["OPENAI_API_KEY"]
    if secrets.get("REDIS_PASSWORD"):
        settings.REDIS_PASSWORD = secrets["REDIS_PASSWORD"]
    if secrets.get("LANGCACHE_API_KEY"):
        settings.LANGCACHE_API_KEY = secrets["LANGCACHE_API_KEY"]
    if secrets.get("PINECONE_API_KEY"):
        settings.PINECONE_API_KEY = secrets["PINECONE_API_KEY"]
    
    logger.info("Secrets loaded", keys=list(secrets.keys()))


def get_secret(key: str, default: str = "") -> str:
    """Get secret value with fallback"""
    # Check environment variables first
    value = os.getenv(key, "")
    if value:
        return value
    
    # Check settings
    return getattr(settings, key, default)

