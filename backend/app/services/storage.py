"""
File storage service for S3
"""
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import structlog
from typing import Optional
import uuid

logger = structlog.get_logger()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
) if settings.AWS_ACCESS_KEY_ID else None


async def upload_file(
    file_content: bytes,
    file_name: str,
    user_id: str,
    folder: str = "documents"
) -> Optional[str]:
    """
    Upload file to S3
    
    Args:
        file_content: File content as bytes
        file_name: Original file name
        user_id: User ID
        folder: S3 folder path
        
    Returns:
        S3 URL or None if upload fails
    """
    if not s3_client:
        logger.warning("S3 client not configured, skipping upload")
        return None
    
    try:
        # Generate unique file name
        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
        unique_name = f"{folder}/{user_id}/{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=unique_name,
            Body=file_content,
            ContentType=get_content_type(file_extension),
        )
        
        # Generate URL
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_name}"
        
        logger.info("File uploaded to S3", file_name=unique_name, user_id=user_id)
        return url
        
    except ClientError as e:
        logger.error("S3 upload failed", error=str(e))
        return None


def get_content_type(extension: str) -> str:
    """Get content type from file extension"""
    content_types = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webm': 'audio/webm',
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
    }
    return content_types.get(extension.lower(), 'application/octet-stream')


async def generate_presigned_url(
    file_key: str,
    expiration: int = None
) -> Optional[str]:
    """
    Generate presigned URL for file access
    
    Args:
        file_key: S3 object key
        expiration: URL expiration in seconds
        
    Returns:
        Presigned URL or None
    """
    if not s3_client:
        return None
    
    try:
        expiration = expiration or settings.S3_PRESIGNED_URL_EXPIRATION
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        logger.error("Presigned URL generation failed", error=str(e))
        return None

