"""
Enhanced retrieval system with:
- Endee vector search
- Definition boosting
- Cross-reference expansion
- Reranking
"""
from sentence_transformers import SentenceTransformer
from endee import Endee
from agent_router import detect_acts_from_query
from chunk_lookup import get_lookup
from cross_references import expand_with_definitions, expand_with_references
from reranker import rerank_results
from confidence_scorer import calculate_confidence
from error_handler import logger, safe_execute
from typing import Dict, Optional

# Initialize resources
client = Endee()
model = SentenceTransformer('all-MiniLM-L6-v2')
lookup = get_lookup()

@safe_execute
def retrieve_direct(
    query_text: str,
    n_results: int = 5,
    enable_rerank: bool = True,
    enable_definitions: bool = True
) -> Dict:
    """
    Core retrieval function using Endee vector search
    
    Args:
        query_text: User query
        n_results: Number of results to return
        enable_rerank: Whether to use cross-encoder reranking
        enable_definitions: Whether to add definition sections
    
    Returns:
        {
            "documents": [...],
            "metadatas": [...],
            "scores": [...]  (if reranking enabled)
        }
    """
    # Detect relevant acts
    acts_to_search = detect_acts_from_query(query_text)
    act_indexes = [f"{act}_sections" for act in acts_to_search]
    
    logger.info(f"Searching acts: {acts_to_search}")
    
    results = {"documents": [], "metadatas": [], "scores": []}
    
    # Embed query
    query_vector = model.encode(query_text).tolist()
    
    # Search each act index
    for index_name in act_indexes:
        try:
            index = client.get_index(name=index_name)
            
            # Get more results if we're going to rerank
            fetch_k = n_results * 3 if enable_rerank else n_results
            
            search_res = index.query(vector=query_vector, top_k=fetch_k)
            
            # Parse results
            for hit in search_res:
                chunk_id = hit.get('id')
                meta = hit.get('meta', {})
                score = hit.get('score', 0.0)
                
                # Fetch full content from ID map
                act = meta.get('act', '').lower()
                chunk = lookup.get_chunk(chunk_id)
                
                if chunk:
                    results["documents"].append(chunk['content'])
                    results["metadatas"].append({
                        'section': chunk.get('section', ''),
                        'section_display': chunk.get('section_display', f"Section {chunk.get('section', '')}"),
                        'heading': chunk.get('heading', ''),
                        'chapter': chunk.get('chapter', ''),
                        'act': act.upper()
                    })
                    results["scores"].append(float(score))
                else:
                    logger.warning(f"Chunk not found in lookup: {chunk_id}")
                    
        except Exception as e:
            logger.error(f"Search error on {index_name}: {e}")
    
    # Apply reranking if enabled
    if enable_rerank and results["documents"]:
        results = rerank_results(query_text, results, top_k=n_results)
    
    # Add definition sections if enabled
    if enable_definitions:
        results = expand_with_definitions(query_text, results, max_definitions=2)
    
    logger.info(f"Retrieved {len(results['documents'])} documents")
    
    return results

def retrieve_with_intelligence(
    query_text: str,
    query_type: str = "direct",
    scenario_data: Optional[Dict] = None,
    n_results: int = 5
) -> Dict:
    """
    Intelligent retrieval that uses scenario data and concept expansion
    
    This is the NEW function that integrates everything
    """
    from concept_expander import expand_offenses_hierarchical
    
    # Build enhanced query
    if query_type == "scenario" and scenario_data:
        # Extract offenses
        primary = scenario_data.get("primary_offense", "")
        related = scenario_data.get("related_offenses", [])
        offenses = [primary] + related
        
        # Expand with hierarchical relationships
        expanded = expand_offenses_hierarchical(offenses)
        
        # Build combined query
        search_terms = [primary]
        search_terms.extend(expanded.get("synonyms", [])[:3])
        search_terms.extend(scenario_data.get("actions", [])[:2])
        
        enhanced_query = " ".join(filter(None, search_terms))
        logger.info(f"Enhanced query: {enhanced_query}")
    else:
        enhanced_query = query_text
    
    # Retrieve
    results = retrieve_direct(
        enhanced_query,
        n_results=n_results,
        enable_rerank=True,
        enable_definitions=True
    )
    
    # Add cross-references (if your chunks have reference data)
    results = expand_with_references(results, max_expand=2)
    
    return results

# Legacy function for compatibility
def retrieve_parallel(concepts, collection=None, query_text=""):
    """Deprecated - use retrieve_with_intelligence instead"""
    logger.warning("retrieve_parallel is deprecated, use retrieve_with_intelligence")
    return retrieve_direct(query_text, n_results=5)