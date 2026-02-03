import sys
import os

# 1. Setup path so we can import from 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentence_transformers import SentenceTransformer
from app.endee_client import search_vector

# 2. Configuration
model = SentenceTransformer('all-MiniLM-L6-v2')

# Test cases: (Index Name, Query Text)
TEST_QUERIES = [
    ("bns_sections", "punishment for mob lynching"),
    ("ipc_sections", "definition of theft"),
    ("crpc_sections", "procedure for arrest"),
    ("bsa_sections", "electronic evidence admissibility")
]

# ... (imports remain the same)

def run_verification():
    print("🔎 Verifying Endee Search (MsgPack Mode)...\n")
    
    for index_name, query_text in TEST_QUERIES:
        print(f"--- Testing Index: {index_name} ---")
        print(f"Query: '{query_text}'")
        
        try:
            query_vector = model.encode([query_text]).tolist()[0]
            results = search_vector(index_name, query_vector, top_k=1)
            
            if results:
                top_result = results[0]
                meta = top_result.get('meta', {})
                
                # Check where the text is stored (it might be in 'document' or 'text_content')
                doc_text = meta.get('document', meta.get('text', 'No Text Found'))
                
                print(f"✅ FOUND: {len(results)} result(s)")
                print(f"   Score: {top_result.get('score', 0)}")
                print(f"   Section: {meta.get('section_display', 'N/A')}")
                print(f"   Snippet: {str(doc_text)[:100]}...\n")
            else:
                print(f"❌ NO RESULTS FOUND.\n")
                
        except Exception as e:
            print(f"🔥 ERROR: {e}\n")

if __name__ == "__main__":
    run_verification()