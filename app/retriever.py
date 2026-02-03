from tqdm import tqdm
from agent_router import detect_acts_from_query
from sentence_transformers import SentenceTransformer
from endee import Endee # Official SDK

# Initialize SDK
client = Endee()
model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_direct(query_text: str, n_results: int = 5):
    """
    Retrieves legal sections using the official Endee SDK
    """
    acts_to_search = detect_acts_from_query(query_text)
    act_indexes = [f"{act}_sections" for act in acts_to_search]

    results = {"documents": [], "metadatas": []}
    query_vector = model.encode(query_text).tolist()

    for index_name in act_indexes:
        try:
            # Get Index
            index = client.get_index(name=index_name)
            
            # Search (SDK handles serialization automatically)
            search_res = index.query(vector=query_vector, top_k=n_results)
            
            # Parse SDK Results
            # Structure usually: [{'id':..., 'score':..., 'meta':...}]
            for hit in search_res:
                meta = hit.get('meta', {})
                doc_content = meta.get('document', '')
                
                if doc_content:
                    results["documents"].append(doc_content)
                    # Clean meta for UI display
                    clean_meta = {k: v for k, v in meta.items() if k != 'document'}
                    results["metadatas"].append(clean_meta)
                    
        except Exception as e:
            print(f"Search error on {index_name}: {e}")

    return results

# Keep parallel version for compatibility if needed
def retrieve_parallel(concepts, collection=None, query_text=""):
    """
    Wrapper for complex queries - simplifies to direct retrieval for this assignment
    """
    # For the assignment scope, searching the primary query is usually sufficient 
    # and safer than threading with the new SDK until tested.
    return retrieve_direct(query_text, n_results=5)