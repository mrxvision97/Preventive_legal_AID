"""
RAG (Retrieval Augmented Generation) Service
"""
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from app.core.config import settings
import structlog
import tiktoken

logger = structlog.get_logger()

# Initialize embeddings
embeddings = OpenAIEmbeddings(
    model=settings.OPENAI_EMBEDDING_MODEL,
    openai_api_key=settings.OPENAI_API_KEY,
)

# Text splitter configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,  # 512 tokens
    chunk_overlap=50,  # 50 token overlap
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def split_document(text: str) -> List[str]:
    """Split document into chunks"""
    chunks = text_splitter.split_text(text)
    return chunks


async def generate_embeddings(text: str) -> List[float]:
    """Generate embeddings for text"""
    try:
        embedding = await embeddings.aembed_query(text)
        return embedding
    except Exception as e:
        logger.error("Embedding generation failed", error=str(e))
        raise


async def retrieve_relevant_context(
    query: str,
    domain: str,
    top_k: int = 10,
    location_filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context from vector database
    
    Args:
        query: User query
        domain: Legal domain filter
        top_k: Number of chunks to retrieve
        location_filter: Location-based filter
        
    Returns:
        List of relevant chunks with metadata
    """
    try:
        # Generate query embedding
        query_embedding = await generate_embeddings(query)
        
        # Search vector database (Pinecone or Weaviate)
        # This is a placeholder - implement actual vector DB search
        results = await search_vector_db(
            query_embedding,
            domain=domain,
            top_k=top_k,
            location_filter=location_filter
        )
        
        # Re-rank results (simplified - use proper re-ranking in production)
        ranked_results = rank_results(query, results)
        
        # Return top 5 most relevant
        return ranked_results[:5]
        
    except Exception as e:
        logger.error("RAG retrieval failed", error=str(e))
        return []


async def search_vector_db(
    query_embedding: List[float],
    domain: str,
    top_k: int = 10,
    location_filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search vector database using Pinecone
    """
    from app.services.pinecone_service import query_vectors
    
    # Build filter for domain
    filter_dict = {"domain": domain}
    if location_filter:
        if location_filter.get("state"):
            filter_dict["state"] = location_filter["state"]
    
    # Query Pinecone
    results = await query_vectors(
        query_vector=query_embedding,
        top_k=top_k,
        filter=filter_dict if filter_dict else None
    )
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            "text": result["metadata"].get("text", ""),
            "score": result["score"],
            "metadata": result["metadata"]
        })
    
    return formatted_results


def rank_results(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Re-rank results based on relevance"""
    # Simplified ranking - use proper re-ranking model in production
    return sorted(results, key=lambda x: x.get("score", 0), reverse=True)


async def index_document(
    text: str,
    metadata: Dict[str, Any],
    domain: str
) -> bool:
    """
    Index a document in the vector database
    
    Args:
        text: Document text
        metadata: Document metadata
        domain: Legal domain
        
    Returns:
        Success status
    """
    try:
        # Split document into chunks
        chunks = split_document(text)
        
        # Generate embeddings for each chunk
        chunk_embeddings = []
        for chunk in chunks:
            embedding = await generate_embeddings(chunk)
            chunk_embeddings.append({
                "text": chunk,
                "embedding": embedding,
                "metadata": {
                    **metadata,
                    "domain": domain,
                    "chunk_index": chunks.index(chunk),
                }
            })
        
        # Store in vector database using Pinecone
        from app.services.pinecone_service import upsert_vectors
        
        vectors = []
        for chunk_data in chunk_embeddings:
            vectors.append({
                "id": f"{metadata.get('source', 'unknown')}_{chunk_data['metadata']['chunk_index']}",
                "values": chunk_data["embedding"],
                "metadata": chunk_data["metadata"]
            })
        
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            await upsert_vectors(batch, namespace=domain)
        
        logger.info("Document indexed", domain=domain, chunks=len(chunks))
        
        return True
        
    except Exception as e:
        logger.error("Document indexing failed", error=str(e))
        return False

