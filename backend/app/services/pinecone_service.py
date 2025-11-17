"""
Pinecone vector database service
"""
from typing import List, Dict, Any, Optional
try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    Pinecone = None
    ServerlessSpec = None
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Initialize Pinecone client
pinecone_client: Optional[Pinecone] = None
index = None


async def init_pinecone():
    """Initialize Pinecone connection and index"""
    global pinecone_client, index
    
    if not Pinecone:
        logger.warning("Pinecone library not installed")
        return
    
    if not settings.PINECONE_API_KEY:
        logger.warning("Pinecone API key not configured")
        return
    
    try:
        pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Check if index exists, create if not
        existing_indexes = [idx.name for idx in pinecone_client.list_indexes()]
        
        if settings.PINECONE_INDEX_NAME not in existing_indexes:
            logger.info("Creating Pinecone index", index_name=settings.PINECONE_INDEX_NAME)
            pinecone_client.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=3072,  # text-embedding-3-large dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.PINECONE_ENVIRONMENT
                )
            )
        
        index = pinecone_client.Index(settings.PINECONE_INDEX_NAME)
        logger.info("Pinecone initialized successfully", index_name=settings.PINECONE_INDEX_NAME)
        
    except Exception as e:
        logger.error("Pinecone initialization failed", error=str(e))
        raise


async def upsert_vectors(
    vectors: List[Dict[str, Any]],
    namespace: Optional[str] = None
) -> bool:
    """
    Upsert vectors to Pinecone
    
    Args:
        vectors: List of dicts with 'id', 'values', and 'metadata'
        namespace: Optional namespace for the vectors
        
    Returns:
        Success status
    """
    if not index:
        logger.error("Pinecone index not initialized")
        return False
    
    try:
        index.upsert(vectors=vectors, namespace=namespace)
        logger.info("Vectors upserted", count=len(vectors), namespace=namespace)
        return True
    except Exception as e:
        logger.error("Vector upsert failed", error=str(e))
        return False


async def query_vectors(
    query_vector: List[float],
    top_k: int = 10,
    namespace: Optional[str] = None,
    filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Query Pinecone for similar vectors
    
    Args:
        query_vector: Query embedding vector
        top_k: Number of results to return
        namespace: Optional namespace
        filter: Optional metadata filter
        
    Returns:
        List of matching vectors with scores
    """
    if not index:
        logger.error("Pinecone index not initialized")
        return []
    
    try:
        query_response = index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
            filter=filter
        )
        
        results = []
        for match in query_response.matches:
            results.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata or {}
            })
        
        logger.info("Vector query completed", results_count=len(results))
        return results
        
    except Exception as e:
        logger.error("Vector query failed", error=str(e))
        return []


async def delete_vectors(
    ids: List[str],
    namespace: Optional[str] = None
) -> bool:
    """Delete vectors by IDs"""
    if not index:
        return False
    
    try:
        index.delete(ids=ids, namespace=namespace)
        logger.info("Vectors deleted", count=len(ids))
        return True
    except Exception as e:
        logger.error("Vector deletion failed", error=str(e))
        return False

