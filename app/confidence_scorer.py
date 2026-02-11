"""Calculate confidence scores for retrieval results"""
from typing import Dict, List
import numpy as np

def calculate_confidence(
    results: Dict,
    query: str,
    query_type: str = "direct"
) -> Dict:
    """
    Calculate multi-factor confidence score
    
    Returns:
        {
            "score": 0.0-1.0,
            "level": "high"/"medium"/"low",
            "factors": {details}
        }
    """
    confidence = {
        "score": 0.0,
        "level": "low",
        "factors": {}
    }
    
    if not results.get('documents'):
        return confidence
    
    # Factor 1: Number of results found (0.2 weight)
    num_results = len(results['documents'])
    if num_results >= 5:
        confidence['factors']['result_count'] = "excellent"
        confidence['score'] += 0.2
    elif num_results >= 3:
        confidence['factors']['result_count'] = "good"
        confidence['score'] += 0.15
    else:
        confidence['factors']['result_count'] = "limited"
        confidence['score'] += 0.05
    
    # Factor 2: Vector similarity scores if available (0.4 weight)
    if 'scores' in results and results['scores']:
        avg_score = np.mean(results['scores'])
        confidence['factors']['avg_similarity'] = round(float(avg_score), 3)
        
        if avg_score >= 0.7:
            confidence['score'] += 0.4
        elif avg_score >= 0.5:
            confidence['score'] += 0.25
        else:
            confidence['score'] += 0.1
    
    # Factor 3: Act coverage diversity (0.2 weight)
    if results.get('metadatas'):
        unique_acts = len(set(m.get('act', '') for m in results['metadatas']))
        confidence['factors']['acts_covered'] = unique_acts
        
        if unique_acts >= 2:
            confidence['score'] += 0.2
        elif unique_acts == 1:
            confidence['score'] += 0.1
    
    # Factor 4: Query type match (0.2 weight)
    if query_type == "section":
        # Section queries should have high confidence if we found the section
        if any('is_definition' in m for m in results.get('metadatas', [])):
            confidence['factors']['section_match'] = True
            confidence['score'] += 0.2
    else:
        # For scenario/direct queries, check for consensus
        if num_results >= 3:
            confidence['factors']['consensus'] = True
            confidence['score'] += 0.15
    
    # Determine level
    if confidence['score'] >= 0.7:
        confidence['level'] = "high"
    elif confidence['score'] >= 0.4:
        confidence['level'] = "medium"
    else:
        confidence['level'] = "low"
    
    return confidence