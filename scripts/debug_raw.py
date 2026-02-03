import sys
import os
import requests
import json
from sentence_transformers import SentenceTransformer

# Setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
model = SentenceTransformer('all-MiniLM-L6-v2')
BASE_URL = "http://localhost:8080"

def debug_search():
    index_name = "bns_sections"
    query_text = "punishment for mob lynching"
    
    print(f"--- DEBUGGING {index_name} ---")
    
    # 1. Check Info First
    info_res = requests.get(f"{BASE_URL}/api/v1/index/{index_name}/info")
    print(f"Index Info Status: {info_res.status_code}")
    print(f"Index Info Body: {info_res.text}")
    
    if '"total_elements":0' in info_res.text:
        print("❌ STOP: The index is empty. Please run embed_to_endee.py again.")
        return

    # 2. Prepare Vector
    print("\nEncoding query...")
    vector = model.encode([query_text]).tolist()[0]
    
    # 3. Send Search Request (Strict JSON payload from docs)
    payload = {
        "vector": vector,
        "k": 5,
        "include_vectors": True,  # Try TRUE to see if that forces a response
        "with_meta": True
    }
    
    print("\nSending Search Request...")
    # Note: Using stream=True to inspect raw bytes
    res = requests.post(
        f"{BASE_URL}/api/v1/index/{index_name}/search", 
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Search Status Code: {res.status_code}")
    print(f"Response Content Length: {len(res.content)} bytes")
    
    # 4. Print the first 100 bytes in Hex to see if it's JSON or Binary
    print("\n--- RAW RESPONSE START ---")
    print(res.content[:200])
    print("--- RAW RESPONSE END ---")

if __name__ == "__main__":
    debug_search()