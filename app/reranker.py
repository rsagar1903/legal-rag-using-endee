"""Cross-encoder reranking for precision improvement"""
from typing import Dict, List, Tuple
from sentence_transformers import CrossEncoder
from error_handler import logger, safe_execute
import numpy as np

# Initialize cross-encoder (lazy loading)
_cross_encoder = None

def get_cross_encoder():
    """Lazy load cross-encoder model"""
    global _cross_encoder
    if _cross_encoder is None:
        try:
            _cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            logger.info("Cross-encoder loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load cross-encoder: {e}")
            _cross_encoder = None
    return _cross_encoder

@safe_execute
def rerank_results(
    query: str,
    results: Dict,
    top_k: int = 5
) -> Dict:
    """
    Rerank results using cross-encoder for better precision
    
    Args:
        query: User query
        results: Retrieved results from vector search
        top_k: Number of results to return
    
    Returns:
        Reranked results with scores
    """
    cross_encoder = get_cross_encoder()
    
    if not cross_encoder or not results.get('documents'):
        logger.warning("Reranking skipped - returning original results")
        return results
    
    # Create query-document pairs
    pairs = [(query, doc) for doc in results['documents']]
    
    # Get cross-encoder scores
    try:
        scores = cross_encoder.predict(pairs)
        scores = [float(s) for s in scores]  # Convert to Python float
    except Exception as e:
        logger.error(f"Cross-encoder prediction failed: {e}")
        return results
    
    # Combine results with scores
    combined = list(zip(
        results['documents'],
        results['metadatas'],
        scores
    ))
    
    # Sort by score (descending)
    combined.sort(key=lambda x: x[2], reverse=True)
    
    # Take top_k
    combined = combined[:top_k]
    
    # Reconstruct results dict
    reranked = {
        "documents": [item[0] for item in combined],
        "metadatas": [item[1] for item in combined],
        "scores": [item[2] for item in combined]
    }
    
    logger.info(f"Reranked {len(results['documents'])} → {len(reranked['documents'])} results")
    
    return reranked